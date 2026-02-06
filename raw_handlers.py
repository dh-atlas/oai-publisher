from sparql import LIST_IDENTIFIERS_QUERY, LIST_RECORDS_QUERY, GET_RECORD_QUERY
from response import create_base_response, to_json_response, to_pretty_xml
from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime
import xml.etree.ElementTree as ET
from namespaces import *

sparql = SPARQLWrapper(SPARQL_ENDPOINT)
sparql.setReturnFormat(JSON)


# VERB IDENTIFY (NO METADATA PREFIX)
def handler_identify():
    root = create_base_response("Identify")
    identify = ET.SubElement(root, f"{{{OAI_NS}}}Identify")
    ET.SubElement(identify, f"{{{OAI_NS}}}repositoryName").text = OAI_PUBLISHER_NAME
    ET.SubElement(identify, f"{{{OAI_NS}}}baseURL").text = OAI_PUBLISHER_BASE_URL
    ET.SubElement(identify, f"{{{OAI_NS}}}protocolVersion").text = "2.0"
    ET.SubElement(identify, f"{{{OAI_NS}}}adminEmail").text = "admin@example.org"
    ET.SubElement(identify, f"{{{OAI_NS}}}earliestDatestamp").text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    ET.SubElement(identify, f"{{{OAI_NS}}}deletedRecord").text = "no"
    ET.SubElement(identify, f"{{{OAI_NS}}}granularity").text = "YYYY-MM-DDThh:mm:ssZ"
    return to_pretty_xml(root)


def raw_handler_identify():
    return to_json_response({"repositoryName": "SPARQL-Backed OAI-PMH Repository",
                             "baseURL": OAI_PUBLISHER_BASE_URL,
                             "protocolVersion": "2.0", "adminEmail": "admin@example.org",
                             "earliestDatestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                             "deletedRecord": "no",
                             "granularity": "YYYY-MM-DDThh:mm:ssZ"})


# VERB LIST IDENTIFIERS (NO METADATA PREFIX)
def raw_handler_list_identifiers(args):
    sparql.setQuery(LIST_IDENTIFIERS_QUERY)
    results = sparql.query().convert()
    return to_json_response({"verb": "ListIdentifiers", "results": results})


# VERB GET RECORD (NO METADATA PREFIX) 
def raw_handler_get_record(identifier):
    sparql.setQuery(GET_RECORD_QUERY.format(identifier=identifier))
    results = sparql.query().convert()
    return to_json_response({"verb": "getRecord", "results": results})


# VERB LIST MD FORMATS (NO METADATA PREFIX)
def raw_list_metadata_formats(identifier):
    return to_json_response({
        "verb": "ListMetadataFormats",
        "formats": [
            {
                "metadataPrefix": OAI_OPENAIRE_PREFIX,
                "schema": OPENAIRE_SCHEMA_LOCATION,
                "metadataNamespace": OPENAIRE_NS
            }
        ]
    })


# VERB LIST RECORDS (NO METADATA PREFIX)
def raw_handler_list_records(args):
    sparql.setQuery(LIST_RECORDS_QUERY)
    results = sparql.query().convert()
    return to_json_response({"verb": "ListRecords", "results": results})
