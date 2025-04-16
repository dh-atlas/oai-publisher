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
    elif verb == 'myverb':
        return handle_myverb()
        
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

def handle_get_record(identifier, metadataPrefix):
    try:
        # Esegui la query SPARQL per recuperare i metadati del record
        sparql.setQuery(f"""
            SELECT ?title ?creator ?subject ?date ?identifier
            WHERE {{
                ?record dc:identifier "{identifier}" ;
                        dc:title ?title ;
                        dc:creator ?creator ;
                        dc:subject ?subject ;
                        dc:date ?date .
            }}
        """)
        results = sparql.query().convert()

        # Verifica se ci sono risultati
        if not results["results"]["bindings"]:
            raise OAI_PMH_Error("idDoesNotExist", f"Record with identifier {identifier} does not exist.")

        # Estrai i metadati del record
        record = results["results"]["bindings"][0]
        title = record["title"]["value"]
        creator = record["creator"]["value"]
        subject = record["subject"]["value"]
        date = record["date"]["value"]

        # Crea la risposta XML per il record
        root = create_base_response("GetRecord")
        GetRecord_elem = ET.SubElement(root, "{" + OAI_NS + "}GetRecord")
        ET.SubElement(GetRecord_elem, "{" + OAI_NS + "}recordIdentifier").text = identifier

        metadata_elem = ET.SubElement(GetRecord_elem, "{" + OAI_NS + "}metadata")
        oai_dc_elem = ET.SubElement(metadata_elem, "{" + OAI_DC_NS + "}oai_dc")

        ET.SubElement(oai_dc_elem, "dc:title").text = title
        ET.SubElement(oai_dc_elem, "dc:creator").text = creator
        ET.SubElement(oai_dc_elem, "dc:subject").text = subject
        ET.SubElement(oai_dc_elem, "dc:date").text = date

        # Restituisci la risposta XML
        response_xml = ET.tostring(root, encoding="utf-8", method="xml")
        return Response(response_xml, content_type='text/xml')

    except OAI_PMH_Error as e:
        # Gestisci l'errore se il record non esiste
        error_response = create_base_response("GetRecord")
        error_elem = ET.SubElement(error_response, "{" + OAI_NS + "}error")
        error_elem.set("code", e.code)
        error_elem.text = e.message

        error_xml = ET.tostring(error_response, encoding="utf-8", method="xml")
        return Response(error_xml, content_type='text/xml', status=400)
        
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

#MYVERB TO PLAY WITH
def handle_myverb():
    # Creazione della risposta di base per myverb
    root = create_base_response("myverb")
    myverb_elem = ET.SubElement(root, "{" + OAI_NS + "}myverb")

    # Costruzione della query SPARQL
    sparql_query = """
        PREFIX ns1: <http://schema.org/>

        SELECT ?s ?p ?o
        WHERE {
            ?s ns1:description ?desc .
            FILTER CONTAINS(STR(?desc), "Zeri&LODE") .
            ?s ?p ?o .
        }
    """

    # Esegui la query SPARQL
    sparql.setQuery(sparql_query)
    results = sparql.query().convert()

    # Verifica se ci sono risultati
    if not results["results"]["bindings"]:
        raise Exception("No records found with description containing 'Zeri&LODE'.")

    # Raggruppa i risultati per soggetto
    grouped_results = {}
    for result in results["results"]["bindings"]:
        s = result["s"]["value"]
        p = result["p"]["value"]
        o = result["o"]["value"]
        grouped_results.setdefault(s, []).append((p, o))

    # Costruisci l'XML con i risultati
    for s, props in grouped_results.items():
        record_elem = ET.SubElement(myverb_elem, "{" + OAI_NS + "}record")
        ET.SubElement(record_elem, "{" + OAI_NS + "}identifier").text = s
        metadata_elem = ET.SubElement(record_elem, "{" + OAI_NS + "}metadata")
        for p, o in props:
            prop_elem = ET.SubElement(metadata_elem, "property")
            ET.SubElement(prop_elem, "predicate").text = p
            ET.SubElement(prop_elem, "object").text = o

    # Serializzazione XML con indentazione
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

