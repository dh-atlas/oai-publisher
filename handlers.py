from sparql import LIST_IDENTIFIERS_QUERY, LIST_RECORDS_QUERY, GET_RECORD_QUERY
from response import create_base_response, to_pretty_xml, to_json_response, handle_oai_error, OAI_PMH_Error
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
    DATACITE_NS,
    DATACITE_KERNEL_NS,
    DC_NS,
    OAIRE_NS,
    DATACITE_SCHEMA_LOCATION,
    OAI_SPARQL_BE,
    OAI_OAIRE_PF,
    OAI_DC_PF,
    DATACITE_ET,
    DC_ET,
    OAIRE_ET
)

sparql = SPARQLWrapper(SPARQL_ENDPOINT)
sparql.setReturnFormat(JSON)

""" IDENTIFY """


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


""" LISTIDENTIFIERS """


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


""" LIST RECORDS """


def handler_list_records(metadata_prefix):
    if metadata_prefix is None:  # no metadataPrexif to test SPARQL results with default namespace
        return handler_list_records_no_mp()
    else:
        return handler_list_records_mp(metadata_prefix)


def handler_list_records_no_mp():
    # base XML for OAI-PMH ListRecords structure
    root = create_base_response("ListRecords")
    list_records_elem = ET.SubElement(root, f"{{{OAI_NS}}}ListRecords")

    # query
    sparql.setQuery(LIST_RECORDS_QUERY)
    results = sparql.query().convert()

    if not results["results"]["bindings"]:
        raise Exception("No records found.")

    # loop over records
    for row in results["results"]["bindings"]:
        record_elem = ET.SubElement(list_records_elem, f"{{{OAI_NS}}}record")

        header_elem = ET.SubElement(record_elem, f"{{{OAI_NS}}}header")
        ET.SubElement(header_elem, f"{{{OAI_NS}}}identifier").text = row["dataset"]["value"]
        ET.SubElement(header_elem, f"{{{OAI_NS}}}datestamp").text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        metadata_elem = ET.SubElement(record_elem, f"{{{OAI_NS}}}metadata")

        def add_metadata(tag, varname):
            if varname in row:
                ET.SubElement(metadata_elem, tag).text = row[varname]["value"]

        for k, v in SPARQL_STD_DICT.items():
            add_metadata(k, v)  # ,OAI_NS)

    # serialize in indented XML
    return to_pretty_xml(root)


####

def handler_list_records_mp(metadata_prefix: str):
    if metadata_prefix == OAI_DATACITE_PF:
        return list_records_oai_datacite()


def list_records_oai_datacite_1():
    # Get data from SPARQL
    # base XML for OAI-PMH ListRecords structure
    root = create_base_response("ListRecords")
    list_records_elem = ET.SubElement(root, f"{{{OAI_NS}}}ListRecords")

    # query
    sparql.setQuery(LIST_RECORDS_QUERY)
    results = sparql.query().convert()
    # Create XML response with proper headers
    root, metadata, datacite = create_oai_datacite_header()
    if not results["results"]["bindings"]:
        raise Exception("No records found.")

    # loop over records
    i = 1
    list_records = ET.SubElement(root, "ListRecords")

    for row in results["results"]["bindings"]:
        print("i= ", i)

        # Add record header
        record = ET.SubElement(list_records, "record")
        header = ET.SubElement(record, "header")
        # Add identifier
        id_element = ET.SubElement(header, "identifier")  # add identifierType=URI
        identifier = row["dataset"]["value"]
        id_element.text = identifier
        datacite_identifier = ET.SubElement(datacite, "datacite:identifier", {"identifierType": "URI"})
        datacite_identifier.text = identifier
        # Add datestamp
        datestamp = ET.SubElement(header, "datestamp")
        datestamp.text = row.get("dateModified", {}).get("value", datetime.utcnow().strftime("%Y-%m-%d"))

        # Attach metadata element to record
        record.append(metadata)

        # Process all fields according to mapping dictionaries
        for source_field, target_fields in DATACITE_TO_STD_DICT.items():

            for target_field in target_fields:
                # Get the corresponding SPARQL field name
                print(source_field, target_fields)
                sparql_field = SPARQL_STD_DICT.get(target_field)
                if sparql_field and sparql_field in row:
                    # Create element with appropriate namespace
                    if source_field.startswith(OAI_DATACITE_PF):
                        field_name = source_field.split(':')[1]
                        element = ET.SubElement(datacite, DATACITE_ET + field_name)
                    elif source_field.startswith(OAI_DC_PF):
                        field_name = source_field.split(':')[1]
                        element = ET.SubElement(datacite, DC_ET + field_name)
                    elif source_field.startswith(OAI_OAIRE_PF):
                        field_name = source_field.split(':')[1]
                        element = ET.SubElement(datacite, OAIRE_ET + field_name)
                    else:
                        element = ET.SubElement(datacite, source_field)

                    # Set the value from SPARQL results
                    element.text = row[sparql_field]["value"]

        i = i + 1
    return to_pretty_xml(root)


def list_records_oai_datacite():
    # Create base OAI-PMH response with proper headers
    root = create_base_response("ListRecords")

    # Create ListRecords element only once
    list_records = ET.SubElement(root, "ListRecords")

    # Query data from SPARQL
    sparql.setQuery(LIST_RECORDS_QUERY)
    results = sparql.query().convert()

    if not results["results"]["bindings"]:
        raise Exception("No records found.")

    # Process each record
    for row in results["results"]["bindings"]:
        # Create new record element
        record = ET.SubElement(list_records, "record")

        # Add header
        header = ET.SubElement(record, "header")

        # Add identifier to header
        identifier = row["dataset"]["value"]
        id_element = ET.SubElement(header, "identifier")
        id_element.text = identifier

        # Add datestamp to header
        datestamp = ET.SubElement(header, "datestamp")
        datestamp.text = row.get("dateModified", {}).get("value", datetime.utcnow().strftime("%Y-%m-%d"))

        # Create new metadata element for this record
        metadata = ET.SubElement(record, "metadata")

        # Create new oai_datacite element for this record
        datacite = ET.SubElement(metadata, "oai_datacite", {
            "xmlns": DATACITE_NS,
            "xmlns:datacite": DATACITE_KERNEL_NS,
            "xmlns:dc": DC_NS,
            "xmlns:oaire": OAIRE_NS,
            "xsi:schemaLocation": f"{DATACITE_NS} {DATACITE_SCHEMA_LOCATION}"
        })

        # Add datacite identifier
        datacite_identifier = ET.SubElement(datacite, "datacite:identifier", {"identifierType": "URI"})
        datacite_identifier.text = identifier

        # Process all fields according to mapping dictionaries
        for source_field, target_fields in DATACITE_TO_STD_DICT.items():
            for target_field in target_fields:
                # Get the corresponding SPARQL field name
                sparql_field = SPARQL_STD_DICT.get(target_field)
                if sparql_field and sparql_field in row:
                    # Create element with appropriate namespace
                    if source_field.startswith(OAI_DATACITE_PF):
                        field_name = source_field.split(':')[1]
                        element = ET.SubElement(datacite, DATACITE_ET + field_name)
                    elif source_field.startswith(OAI_DC_PF):
                        field_name = source_field.split(':')[1]
                        element = ET.SubElement(datacite, DC_ET + field_name)
                    elif source_field.startswith(OAI_OAIRE_PF):
                        field_name = source_field.split(':')[1]
                        element = ET.SubElement(datacite, OAIRE_ET + field_name)
                    else:
                        element = ET.SubElement(datacite, source_field)

                    # Set the value from SPARQL results
                    element.text = row[sparql_field]["value"]

    return to_pretty_xml(root)


####


""" GET RECORD """


def handler_get_record(identifier: str, metadata_prefix: str):
    # metadataPrefix logic
    if metadata_prefix is None:  # no metadataPrexif to test SPARQL results with default namespace
        return handler_get_record_no_mp(identifier)
    else:
        return handler_get_record_mp(identifier, metadata_prefix)


def handler_get_record_no_mp(identifier: str):
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

    def add_element(tag, key, ns):
        if key in row:
            ET.SubElement(metadata_elem, f"{{{ns}}}{tag}").text = row[key]["value"]

    print(SPARQL_STD_DICT.keys())
    for k, v in SPARQL_STD_DICT.items():
        add_element(k, v, OAI_NS)

    # Campi da aggiungere
    '''add_element("title", "names")
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
    '''

    return to_pretty_xml(root)


def handler_get_record_mp(identifier: str, metadata_prefix: str):
    if metadata_prefix == OAI_DATACITE_PF:
        return get_record_oai_datacite(identifier)


def get_record_oai_datacite(identifier):
    # Get data from SPARQL
    sparql.setQuery(GET_RECORD_QUERY.format(identifier=identifier))
    results = sparql.query().convert()
    bindings = results["results"]["bindings"]
    if not bindings:
        raise OAI_PMH_Error("idDoesNotExist", f"No records found for identifier {identifier}")

    row = bindings[0]

    # Create XML response with proper headers
    root, metadata, datacite = create_oai_datacite_header()

    # Add record header
    record = ET.SubElement(root, "record")
    header = ET.SubElement(record, "header")

    # Add identifier
    id_element = ET.SubElement(header, "identifier")  # add identifierType=URI
    id_element.text = identifier
    datacite_identifier = ET.SubElement(datacite, "datacite:identifier", {"identifierType": "URI"})
    datacite_identifier.text = identifier

    # Add datestamp
    datestamp = ET.SubElement(header, "datestamp")
    datestamp.text = row.get("dateModified", {}).get("value", datetime.utcnow().strftime("%Y-%m-%d"))

    # Attach metadata element to record
    record.append(metadata)

    # Process all fields according to mapping dictionaries
    for source_field, target_fields in DATACITE_TO_STD_DICT.items():
        for target_field in target_fields:
            # Get the corresponding SPARQL field name
            print(source_field, target_fields)
            sparql_field = SPARQL_STD_DICT.get(target_field)
            if sparql_field and sparql_field in row:
                # Create element with appropriate namespace
                if source_field.startswith(OAI_DATACITE_PF):
                    field_name = source_field.split(':')[1]
                    element = ET.SubElement(datacite, DATACITE_ET + field_name)
                elif source_field.startswith(OAI_DC_PF):
                    field_name = source_field.split(':')[1]
                    element = ET.SubElement(datacite, DC_ET + field_name)
                elif source_field.startswith(OAI_OAIRE_PF):
                    field_name = source_field.split(':')[1]
                    element = ET.SubElement(datacite, OAIRE_ET + field_name)
                else:
                    element = ET.SubElement(datacite, source_field)

                # Set the value from SPARQL results
                element.text = row[sparql_field]["value"]

    return to_pretty_xml(root)


def create_oai_datacite_header():
    # Create the root element with all necessary namespace declarations
    root = ET.Element("OAI-PMH", {
        "xmlns": OAI_NS,
        "xmlns:xsi": XSI_NS,
        "xsi:schemaLocation": f"{OAI_NS} {OAI_SCHEMA_LOCATION}"
    })

    # Add response date
    response_date = ET.SubElement(root, "responseDate")
    response_date.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # Create the metadata element with specific datacite namespaces
    metadata = ET.Element("metadata")
    datacite = ET.SubElement(metadata, "oai_datacite", {
        "xmlns": DATACITE_NS,
        "xmlns:datacite": DATACITE_KERNEL_NS,
        "xmlns:dc": DC_NS,
        "xmlns:oaire": OAIRE_NS,
        "xsi:schemaLocation": f"{DATACITE_NS} {DATACITE_SCHEMA_LOCATION}"
    })

    return root, metadata, datacite


""" LIST METADATA FORMAT """


def list_metadata_formats(args):
    root = create_base_response("ListMetadataFormats")
    list_formats = SubElement(root, f"{{{OAI_NS}}}ListMetadataFormats")

    format_el = SubElement(list_formats, f"{{{OAI_NS}}}metadataFormat")
    SubElement(format_el, f"{{{OAI_NS}}}metadataPrefix").text = OAI_DATACITE_PF
    SubElement(format_el, f"{{{OAI_NS}}}schema").text = DATACITE_SCHEMA_LOCATION
    SubElement(format_el, f"{{{OAI_NS}}}metadataNamespace").text = DATACITE_NS

    return to_pretty_xml(root)
