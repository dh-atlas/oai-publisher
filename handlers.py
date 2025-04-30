from sparql import LIST_IDENTIFIERS_QUERY, LIST_RECORDS_QUERY,GET_RECORD_QUERY
from response import create_base_response, to_pretty_xml, to_json_response, handle_oai_error, OAI_PMH_Error
from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime
import xml.etree.ElementTree as ET


SPARQL_ENDPOINT = "http://localhost:9999/bigdata/sparql"
OAI_NS = "http://www.openarchives.org/OAI/2.0/"

OAI_NS = "http://www.openarchives.org/OAI/2.0/"
SPARQL_ENDPOINT = "http://localhost:9999/bigdata/sparql"

sparql = SPARQLWrapper(SPARQL_ENDPOINT)
sparql.setReturnFormat(JSON)


def handler_identify():
    root = create_base_response("Identify")
    identify = ET.SubElement(root, f"{{{OAI_NS}}}Identify")
    ET.SubElement(identify, f"{{{OAI_NS}}}repositoryName").text = "SPARQL-Backed OAI-PMH Repository"
    ET.SubElement(identify, f"{{{OAI_NS}}}baseURL").text = "http://localhost:5000/oai"
    ET.SubElement(identify, f"{{{OAI_NS}}}protocolVersion").text = "2.0"
    ET.SubElement(identify, f"{{{OAI_NS}}}adminEmail").text = "admin@example.org"
    ET.SubElement(identify, f"{{{OAI_NS}}}earliestDatestamp").text = "2000-01-01T00:00:00Z"
    ET.SubElement(identify, f"{{{OAI_NS}}}deletedRecord").text = "no"
    ET.SubElement(identify, f"{{{OAI_NS}}}granularity").text = "YYYY-MM-DDThh:mm:ssZ"
    return to_pretty_xml(root)


def raw_handler_identify():
    return to_json_response({"repositoryName": "SPARQL-Backed OAI-PMH Repository"})

'''
def handler_list_identifiers(args):
    root = create_base_response("ListIdentifiers")
    list_elem = ET.SubElement(root, f"{{{OAI_NS}}}ListIdentifiers")
    sparql.setQuery(LIST_IDENTIFIERS_QUERY)
    results = sparql.query().convert()

    for r in results["results"]["bindings"]:
        h = ET.SubElement(list_elem, f"{{{OAI_NS}}}header")
        ET.SubElement(h, f"{{{OAI_NS}}}identifier").text = r["id"]["value"]
        ET.SubElement(h, f"{{{OAI_NS}}}datestamp").text = datetime.utcnow().isoformat() + "Z"
        ET.SubElement(h, f"{{{OAI_NS}}}setSpec").text = r["type"]["value"]
    return to_pretty_xml(root)
 '''
 
def handler_list_identifiers(args):
    root = create_base_response("ListIdentifiers")
    list_elem = ET.SubElement(root, f"{{{OAI_NS}}}ListIdentifiers")
    sparql.setQuery(LIST_IDENTIFIERS_QUERY)
    results = sparql.query().convert()

    for r in results["results"]["bindings"]:
        h = ET.SubElement(list_elem, f"{{{OAI_NS}}}header")
        ET.SubElement(h, f"{{{OAI_NS}}}identifier").text = r["dataset"]["value"]
        ET.SubElement(h, f"{{{OAI_NS}}}datestamp").text = datetime.utcnow().isoformat() + "Z"
    return to_pretty_xml(root)


def raw_handler_list_identifiers(args):
    sparql.setQuery(LIST_IDENTIFIERS_QUERY)
    results = sparql.query().convert()
    return to_json_response(results)


def handler_list_records_dc(args):
    root = create_base_response("ListRecords")
    list_elem = ET.SubElement(root, f"{{{OAI_NS}}}ListRecords")

    sparql.setQuery(LIST_RECORDS_QUERY)
    results = sparql.query().convert()

    for row in results["results"]["bindings"]:
        record_elem = ET.SubElement(list_elem, f"{{{OAI_NS}}}record")

        # HEADER
        header_elem = ET.SubElement(record_elem, f"{{{OAI_NS}}}header")
        ET.SubElement(header_elem, f"{{{OAI_NS}}}identifier").text = row["dataset"]["value"]
        ET.SubElement(header_elem, f"{{{OAI_NS}}}datestamp").text = datetime.utcnow().isoformat() + "Z"

        # METADATA
        metadata_elem = ET.SubElement(record_elem, f"{{{OAI_NS}}}metadata")
        metadata_container = ET.SubElement(metadata_elem, f"{{{OAI_DC_NS}}}dc")

        def add_element(name, key):
            if key in row:
                ET.SubElement(metadata_container, f"{{{DC_NS}}}{name}").text = row[key]["value"]

        # Aggiungi tutti i campi della SELECT
        add_element("title", "names")
        add_element("description", "descriptions")
        add_element("creator", "creators")
        add_element("contributor", "contributors")
        add_element("publisher", "publishers")
        add_element("language", "languages")
        add_element("educationalUse", "educationalUses")
        add_element("relation", "distributions")
        add_element("identifier", "urls")
        add_element("source", "producers")
        add_element("type", "additionalType")
        add_element("date", "datePublished")
        add_element("rights", "conditionsOfAccess")

    return to_pretty_xml(root)


def handler_list_records(args):
    # Crea la struttura base XML per OAI-PMH ListRecords
    root = create_base_response("ListRecords")
    ListRecords_elem = ET.SubElement(root, f"{{{OAI_NS}}}ListRecords")


    # Esegui la query
    sparql.setQuery(LIST_RECORDS_QUERY)
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
    return to_pretty_xml(root)


def raw_handler_list_records(args):
    sparql.setQuery(LIST_RECORDS_QUERY)
    results = sparql.query().convert()
    return to_json_response(results)





def handler_get_record(identifier: str):
    root = create_base_response("GetRecord")
    get_elem = ET.SubElement(root, f"{{{OAI_NS}}}GetRecord")

    sparql.setQuery(GET_RECORD_QUERY.format(identifier=identifier))
    results = sparql.query().convert()
    bindings = results["results"]["bindings"]

    if not bindings:
        raise OAI_PMH_Error("idDoesNotExist", f"No records found for identifier {identifier}")
  
    row = bindings[0]

    # <record>
    record_elem = ET.SubElement(get_elem, f"{{{OAI_NS}}}record")

    # <header>
    header_elem = ET.SubElement(record_elem, f"{{{OAI_NS}}}header")
    ET.SubElement(header_elem, f"{{{OAI_NS}}}identifier").text = row["dataset"]["value"]
    ET.SubElement(header_elem, f"{{{OAI_NS}}}datestamp").text = datetime.utcnow().isoformat() + "Z"

    # <metadata>
    metadata_elem = ET.SubElement(record_elem, f"{{{OAI_NS}}}metadata")

    def add_element(tag, key):
        if key in row:
            ET.SubElement(metadata_elem, f"{{{OAI_NS}}}{tag}").text = row[key]["value"]

    # Campi da aggiungere
    add_element("title", "names")
    add_element("description", "descriptions")
    add_element("creator", "creators")
    add_element("contributor", "contributors")
    add_element("publisher", "publishers")
    add_element("language", "languages")
    add_element("educationalUse", "educationalUses")
    add_element("relation", "distributions")
    add_element("identifier", "urls")
    add_element("source", "producers")
    add_element("type", "additionalType")
    add_element("date", "datePublished")
    add_element("rights", "conditionsOfAccess")

    return to_pretty_xml(root)

def raw_handler_get_record(identifier):
    sparql.setQuery(GET_RECORD_QUERY.format(identifier=identifier))
    results = sparql.query().convert()
    return to_json_response(results)


