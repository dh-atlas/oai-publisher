from sparql import LIST_IDENTIFIERS_QUERY, LIST_RECORDS_QUERY, GET_RECORD_QUERY
from response import create_base_response, to_json_response, handle_oai_error, OAI_PMH_Error, to_pretty_xml
from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import SubElement
from dicts import SPARQL_STD_DICT, DATACITE_TO_STD_DICT
from namespaces import (
    SPARQL_ENDPOINT,
    OAI_NS,
    XSI_NS,
    BASE_URL,
    OAI_SCHEMA_LOCATION,
    OAI_DATACITE_PF,
    OAI_DATACITE_VERSION,
    DATACITE_NS,
    DATACITE_KERNEL_NS,
    DC_NS,
    OAIRE_NS,
    DATACITE_SCHEMA_LOCATION,
    OAI_SPARQL_BE,
    OAI_OAIRE_PF,
    OAI_DATACITE_PF,
    OAI_DC_PF,
    DATACITE_ET,
    DC_ET,
    OAIRE_ET
)

sparql = SPARQLWrapper(SPARQL_ENDPOINT)
sparql.setReturnFormat(JSON)


# VERB IDENTIFY (NO METADATA PREFIX)
def handler_identify():
    root = create_base_response("Identify")
    identify = ET.SubElement(root, f"{{{OAI_NS}}}Identify")
    ET.SubElement(identify, f"{{{OAI_NS}}}repositoryName").text = OAI_SPARQL_BE
    ET.SubElement(identify, f"{{{OAI_NS}}}baseURL").text = BASE_URL
    ET.SubElement(identify, f"{{{OAI_NS}}}protocolVersion").text = "2.0"
    ET.SubElement(identify, f"{{{OAI_NS}}}adminEmail").text = "admin@example.org"
    ET.SubElement(identify, f"{{{OAI_NS}}}earliestDatestamp").text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    ET.SubElement(identify, f"{{{OAI_NS}}}deletedRecord").text = "no"
    ET.SubElement(identify, f"{{{OAI_NS}}}granularity").text = "YYYY-MM-DDThh:mm:ssZ"
    return to_pretty_xml(root)


def raw_handler_identify():
    return to_json_response({"repositoryName": "SPARQL-Backed OAI-PMH Repository",
                             "baseURL": BASE_URL,
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
                "metadataPrefix": OAI_DATACITE_PF,
                "schema": DATACITE_SCHEMA_LOCATION,
                "metadataNamespace": DATACITE_NS
            }
        ]
    })


# VERB LIST RECORDS (NO METADATA PREFIX)
def raw_handler_list_records(args):
    sparql.setQuery(LIST_RECORDS_QUERY)
    results = sparql.query().convert()
    return to_json_response({"verb": "ListRecords", "results": results})
