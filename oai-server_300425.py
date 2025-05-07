from flask import Flask, request, Response
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

from datetime import datetime, timedelta
import uuid
from SPARQLWrapper import SPARQLWrapper, JSON
import os

# init FLASK
app = Flask(__name__)

# OAI PARAMS
REPOSITORY_NAME = "SPARQL-Backed OAI-PMH Repository"
BASE_URL = "http://localhost:5000/oai"
ADMIN_EMAIL = "admin@example.org"
SPARQL_ENDPOINT = "http://localhost:9999/bigdata/sparql"
RECORDS_PER_PAGE = 100


# XML NAMESPACES
OAI_NS = "http://www.openarchives.org/OAI/2.0/"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
DC_NS = "http://purl.org/dc/elements/1.1/"
OAI_DC_NS = "http://www.openarchives.org/OAI/2.0/oai_dc/"
# METTERE OAI_DATACITE


# NAMESPACES REGISTRATION
ET.register_namespace("", OAI_NS)
ET.register_namespace("xsi", XSI_NS)
ET.register_namespace("dc", DC_NS)
ET.register_namespace("oai_dc", OAI_DC_NS)

# SPARQL OBJECTS
sparql = SPARQLWrapper(SPARQL_ENDPOINT)
sparql.setReturnFormat(JSON)

# ERROR CLASS
class OAI_PMH_Error(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(self.message)


def create_base_response(verb):
    root = ET.Element("{" + OAI_NS + "}OAI-PMH")
    root.set("{" + XSI_NS + "}schemaLocation", 
             "http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd")
    
    response_date = ET.SubElement(root, "{" + OAI_NS + "}responseDate")
    response_date.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    request_elem = ET.SubElement(root, "{" + OAI_NS + "}request")
    request_elem.set("verb", verb)
    request_elem.text = BASE_URL
    
    return root

@app.route('/oai', methods=['GET'])
def oai():
    verb = request.args.get('verb')

    if not verb:
        raise OAI_PMH_Error("badVerb", "Missing verb parameter")

    if verb == "Identify":
        return handle_identify()
    
    
    elif verb == 'GetRecord':
        identifier = request.args.get('identifier')
        metadataPrefix = request.args.get('metadataPrefix')    
        handle_get_record(identifier, metadataPrefix)
        
    elif verb == 'ListIdentifiers':
        from_date = request.args.get('from', None)
        until_date = request.args.get('until', None)
        return handle_list_identifiers(from_date, until_date)
    elif verb == "ListRecords":
        return handle_list_records()
        
    raise OAI_PMH_Error("badVerb", f"Unsupported verb: {verb}")
    
# VARIOUS HANDLES 
def handle_identify():
    root = create_base_response("Identify")
    identify_elem = ET.SubElement(root, "{" + OAI_NS + "}Identify")
    
    ET.SubElement(identify_elem, "{" + OAI_NS + "}repositoryName").text = REPOSITORY_NAME
    ET.SubElement(identify_elem, "{" + OAI_NS + "}baseURL").text = BASE_URL
    ET.SubElement(identify_elem, "{" + OAI_NS + "}protocolVersion").text = "2.0"
    ET.SubElement(identify_elem, "{" + OAI_NS + "}adminEmail").text = ADMIN_EMAIL
    ET.SubElement(identify_elem, "{" + OAI_NS + "}earliestDatestamp").text = "2000-01-01T00:00:00Z"
    ET.SubElement(identify_elem, "{" + OAI_NS + "}deletedRecord").text = "no"
    ET.SubElement(identify_elem, "{" + OAI_NS + "}granularity").text = "YYYY-MM-DDThh:mm:ssZ"
    
    # Pretty print dell'XML
    xml_str = ET.tostring(root, encoding="utf-8")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    return Response(pretty_xml, mimetype="text/xml")


        
def handle_list_identifiers(from_date, until_date):
    # Creazione della risposta di base per ListIdentifiers
    root = create_base_response("ListIdentifiers")
    ListIdentifiers_elem = ET.SubElement(root, "{" + OAI_NS + "}ListIdentifiers")
    
    # Costruzione della query SPARQL
    sparql_query = """
        PREFIX schema: <https://schema.org/>
        PREFIX fabio: <http://purl.org/spar/fabio/>
        SELECT ?id ?type
        WHERE {
            ?id a ?type .
            FILTER (?type = schema:Dataset || 
                    ?type = fabio:ComputerProgram || 
                    ?type = fabio:Anthology || 
                    ?type = fabio:MetadataDocument || 
                    ?type = fabio:OntologyDocument || 
                    ?type = fabio:DataFile)
        }
    """
    
    # Se vengono forniti i parametri 'from_date' e 'until_date', aggiungiamo i filtri temporali alla query
    if from_date:
        sparql_query += f" FILTER (?date >= \"{from_date}\")"
    if until_date:
        sparql_query += f" FILTER (?date <= \"{until_date}\")"
    
    # Esegui la query SPARQL
    sparql.setQuery(sparql_query)
    results = sparql.query().convert()

    # Verifica se ci sono risultati
    if not results["results"]["bindings"]:
        raise Exception("No records found matching the specified criteria.")
    
    # Aggiungi gli identificatori e i tipi dei record nella risposta
    for record in results["results"]["bindings"]:
        id_value = record["id"]["value"]
        type_value = record["type"]["value"]
        
        # Crea un elemento <header> per ciascun identificatore
        header_elem = ET.SubElement(ListIdentifiers_elem, "{" + OAI_NS + "}header")
        ET.SubElement(header_elem, "{" + OAI_NS + "}identifier").text = id_value
        ET.SubElement(header_elem, "{" + OAI_NS + "}datestamp").text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Aggiungi anche altre informazioni come il tipo, se necessario
        ET.SubElement(header_elem, "{" + OAI_NS + "}setSpec").text = type_value

    # Restituisci la risposta XML
    xml_str = ET.tostring(root, encoding="utf-8", method="xml")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    return Response(pretty_xml, mimetype="text/xml")
    
# LIST RECORDS
def handle_list_records():
    # Crea la struttura base XML per OAI-PMH ListRecords
    root = create_base_response("ListRecords")
    ListRecords_elem = ET.SubElement(root, f"{{{OAI_NS}}}ListRecords")

    # Definisci la query SPARQL
    sparql_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        
        SELECT ?dataset
          (GROUP_CONCAT(DISTINCT ?name; separator=" || ") AS ?names)
          (GROUP_CONCAT(DISTINCT ?description; separator=" || ") AS ?descriptions)
          (GROUP_CONCAT(DISTINCT ?creator; separator=" || ") AS ?creators)
          (GROUP_CONCAT(DISTINCT ?contributor; separator=" || ") AS ?contributors)
          (GROUP_CONCAT(DISTINCT ?publisher; separator=" || ") AS ?publishers)
          (GROUP_CONCAT(DISTINCT ?inLanguage; separator=" || ") AS ?languages)
          (GROUP_CONCAT(DISTINCT ?educationalUse; separator=" || ") AS ?educationalUses)
          (GROUP_CONCAT(DISTINCT ?distribution; separator=" || ") AS ?distributions)
          (GROUP_CONCAT(DISTINCT ?url; separator=" || ") AS ?urls)
          (GROUP_CONCAT(DISTINCT ?producer; separator=" || ") AS ?producers)
          ?additionalType
          ?datePublished
          ?conditionsOfAccess
        WHERE {
          ?dataset <http://schema.org/name> ?name ; rdf:type <https://schema.org/Dataset> .
          OPTIONAL { ?dataset <http://schema.org/description> ?description . }
          OPTIONAL { ?dataset <http://schema.org/creator> ?creator . }
          OPTIONAL { ?dataset <http://schema.org/publisher> ?publisher . }
          OPTIONAL { ?dataset <http://schema.org/additionalType> ?additionalType . }
          OPTIONAL { ?dataset <http://schema.org/datePublished> ?datePublished . }
          OPTIONAL { ?dataset <http://schema.org/educationalUse> ?educationalUse . }
          OPTIONAL { ?dataset <http://schema.org/distribution> ?distribution . }
          OPTIONAL { ?dataset <http://schema.org/url> ?url . }
          OPTIONAL { ?dataset <http://schema.org/conditionsOfAccess> ?conditionsOfAccess . }
          OPTIONAL { ?dataset <http://schema.org/contributor> ?contributor . }
          OPTIONAL { ?dataset <http://schema.org/inLanguage> ?inLanguage . }
          OPTIONAL { ?dataset <http://schema.org/producer> ?producer . }
        }
        GROUP BY ?additionalType ?datePublished ?conditionsOfAccess ?dataset
    """

    # Esegui la query
    sparql.setQuery(sparql_query)
    results = sparql.query().convert()

    if not results["results"]["bindings"]:
        raise Exception("No records found.")

    # Costruzione XML per ogni record
    for row in results["results"]["bindings"]:
        record_elem = ET.SubElement(ListRecords_elem, f"{{{OAI_NS}}}record")

        header_elem = ET.SubElement(record_elem, f"{{{OAI_NS}}}header")
        ET.SubElement(header_elem, f"{{{OAI_NS}}}identifier").text = row["dataset"]["value"]
        ET.SubElement(header_elem, f"{{{OAI_NS}}}datestamp").text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        metadata_elem = ET.SubElement(record_elem, f"{{{OAI_NS}}}metadata")

        def add_metadata(tag, varname):
            if varname in row:
                ET.SubElement(metadata_elem, tag).text = row[varname]["value"]

        # Aggiungi metadati comuni
        add_metadata("name", "names")
        add_metadata("description", "descriptions")
        add_metadata("creator", "creators")
        add_metadata("publisher", "publishers")
        add_metadata("contributor", "contributors")
        add_metadata("language", "languages")
        add_metadata("educationalUse", "educationalUses")
        add_metadata("distribution", "distributions")
        add_metadata("url", "urls")
        add_metadata("producer", "producers")
        add_metadata("additionalType", "additionalType")
        add_metadata("datePublished", "datePublished")
        add_metadata("conditionsOfAccess", "conditionsOfAccess")

    # Serializza in XML con indentazione
    xml_str = ET.tostring(root, encoding="utf-8", method="xml")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    return Response(pretty_xml, mimetype="text/xml")




@app.errorhandler(OAI_PMH_Error)
def handle_oai_error(error):
    root = create_base_response("error")
    error_elem = ET.SubElement(root, "{" + OAI_NS + "}error")
    error_elem.set("code", error.code)
    error_elem.text = error.message
    
    xml_str = ET.tostring(root, encoding="utf-8")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    return Response(pretty_xml, mimetype="text/xml")

@app.route('/')
def home():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True, port=5000)

