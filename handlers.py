from sparql import LIST_IDENTIFIERS_QUERY, LIST_RECORDS_QUERY, GET_RECORD_QUERY, GET_AGENT_QUERY, GET_PROJECT_QUERY
from response import create_base_response, to_pretty_xml, OAI_PMH_Error
from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import SubElement
from rdflib import Graph, URIRef
from rdflib.namespace import SKOS
from dicts import RIGHTS_DICT, RESOURCE_TYPE_DICT, ATLAS_TO_OPENAIRE, NESTED_ELEMENTS_MAP, SPARQL_STD_DICT
from namespaces import *

sparql = SPARQLWrapper(SPARQL_ENDPOINT)
sparql.setReturnFormat(JSON)

#Licences ttl file upload
g = Graph()
g.parse("licences.ttl", format="ttl")


def get_label(uri, lang="en"):
    uri_ref = URIRef(uri)
    for _, _, label in g.triples((uri_ref, SKOS.prefLabel, None)):
        if label.language == lang:
            return str(label)
    return uri


""" IDENTIFY """


def handler_identify():
    root = create_base_response("Identify")
    identify = ET.SubElement(root, f"{{{OAI_NS}}}Identify")
    ET.SubElement(identify, f"{{{OAI_NS}}}repositoryName").text = OAI_PUBLISHER_NAME
    ET.SubElement(identify, f"{{{OAI_NS}}}baseURL").text = OAI_PUBLISHER_BASE_URL
    ET.SubElement(identify, f"{{{OAI_NS}}}protocolVersion").text = "2.0"
    ET.SubElement(identify, f"{{{OAI_NS}}}deletedRecord").text = "no"
    ET.SubElement(identify, f"{{{OAI_NS}}}granularity").text = "YYYY-MM-DD"  #
    return to_pretty_xml(root)


""" LIST IDENTIFIERS """


def handler_list_identifiers(args):
    root = create_base_response("ListIdentifiers")
    list_elem = ET.SubElement(root, f"{{{OAI_NS}}}ListIdentifiers")
    sparql.setQuery(LIST_IDENTIFIERS_QUERY)
    results = sparql.query().convert()

    for r in results["results"]["bindings"]:
        h = ET.SubElement(list_elem, f"{{{OAI_NS}}}header")
        ET.SubElement(h, f"{{{OAI_NS}}}identifier").text = r["dataset"]["value"]
        ET.SubElement(h, f"{{{OAI_NS}}}datestamp").text = datetime.utcnow().strftime("%Y-%m-%d")
    return to_pretty_xml(root)


# LIST RECORDS

def handler_list_records(metadata_prefix):
    if metadata_prefix is None:
        # no metadataPrexif to test SPARQL results with default namespace
        return handler_list_records_no_mp()
    else:
        return handler_list_records_mp(metadata_prefix)


############## LIST RECORDS NO metadata prefix ##################

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
        ET.SubElement(header_elem, f"{{{OAI_NS}}}datestamp").text = datetime.utcnow().strftime("%Y-%m-%d")

        metadata_elem = ET.SubElement(record_elem, f"{{{OAI_NS}}}metadata")

        def add_metadata(tag, varname):
            if varname in row:
                ET.SubElement(metadata_elem, tag).text = row[varname]["value"]

        for k, v in SPARQL_STD_DICT.items():
            add_metadata(k, v)  # ,OAI_NS)

        ###enter here the fields process according to mapping dictionaries

    # serialize in indented XML
    return to_pretty_xml(root)


############## LIST RECORDS + METADATA PREFIX ##################


def handler_list_records_mp(metadata_prefix: str):
    if metadata_prefix == OAI_OPENAIRE_PREFIX:
        return list_records_oai_openaire()


def list_records_oai_openaire():
    # Create base OAI-PMH response with proper headers
    root = create_base_response("ListRecords")

    print(to_pretty_xml(root))
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

        # Create new oai_openaire element for this record
        datacite = ET.SubElement(metadata, "oaire:resource", {
            "xmlns:datacite": DATACITE_NS,
            "xmlns:dc": DC_NS,
            "xmlns:oaire": OPENAIRE_NS,
            "xsi:schemaLocation": OPENAIRE_SCHEMA_LOCATION
        })

        # Add datacite identifier
        datacite_identifier = ET.SubElement(datacite, "datacite:identifier", {"identifierType": "w3id"})
        datacite_identifier.text = identifier

        return_openaire_record(datacite, row)

    #Count for log
    #print(f"Founded: {num_lic} licenses ({sanity_list_lic}) and {num_access} accesseRights")
    return to_pretty_xml(root)


####


""" SET AGENT """


def set_agent(agents: str, parent_node: SubElement, element_name: str):
    agent_list = agents.split('||')
    for agent in agent_list:
        # Query data from SPARQL
        query = GET_AGENT_QUERY.replace('{identifier}', agent.strip())
        sparql.setQuery(query)
        results = sparql.query().convert()
        for row in results["results"]["bindings"]:
            element = ET.SubElement(parent_node, element_name)
            name = ET.SubElement(element, element_name + 'Name')
            name.text = row['name']["value"]
            if "affName" in row:
                aff = ET.SubElement(element, 'datacite:affiliation')
                aff.text = row['affName']["value"]
            if "orcid" in row:
                orcid = ET.SubElement(element, 'datacite:nameIdentifier', nameIdentifierScheme='ORCID',
                                      schemeURI='http://orcid.org')
                orcid.text = row['orcid']["value"]
            if "wiki" in row:
                wiki = ET.SubElement(element, 'datacite:nameIdentifier', nameIdentifierScheme='WIKI',
                                     schemeURI='http://www.wikidata.org')
                wiki.text = row['wiki']["value"]


""" SET PROJECT """


def set_project(projects: str, parent_node: SubElement, element_name: str):
    project_list = projects.split('||')
    for project in project_list:
        # Query data from SPARQL
        query = GET_PROJECT_QUERY.replace('{identifier}', project.strip())
        sparql.setQuery(query)
        results = sparql.query().convert()
        for row in results["results"]["bindings"]:
            funding_reference = ET.SubElement(parent_node, element_name)
            project_title = row['title']["value"]
            funder_name = row['fundernames']["value"]
            funding_reference_title = ET.SubElement(funding_reference, 'oaire:awardTitle')
            funding_reference_title.text = project_title
            funding_reference_funder_name = ET.SubElement(funding_reference, 'oaire:funderName')
            funding_reference_funder_name.text = funder_name


""" SET PUBLISHER """


def set_publisher(agents: str, parent_node: SubElement):
    agent_list = agents.split('||')
    for agent in agent_list:
        # Query data from SPARQL
        query = GET_AGENT_QUERY.replace('{identifier}', agent.strip())
        sparql.setQuery(query)
        results = sparql.query().convert()
        for row in results["results"]["bindings"]:
            element = ET.SubElement(parent_node, 'dc:publisher')
            element.text = row['name']["value"]


###############################################################################


""" GET RECORD """


# get record metadataprefix

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

    return to_pretty_xml(root)


def handler_get_record_mp(identifier: str, metadata_prefix: str):
    if metadata_prefix == OAI_OPENAIRE_PREFIX:
        return get_record_oai_openaire(identifier)


def get_record_oai_openaire(identifier):
    # Create base OAI-PMH response with proper headers
    root = create_base_response("GetRecord")

    # Create ListRecords element only once
    list_records = ET.SubElement(root, "GetRecord")

    # Query data from SPARQL
    sparql.setQuery(GET_RECORD_QUERY.format(identifier=identifier))
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

        # Create new oai_openaire element for this record
        datacite = ET.SubElement(metadata, "oaire:resource", {
            "xmlns:datacite": DATACITE_NS,
            "xmlns:dc": DC_NS,
            "xmlns:oaire": OPENAIRE_NS,
            "xsi:schemaLocation": OPENAIRE_SCHEMA_LOCATION
        })

        # Add datacite identifier
        datacite_identifier = ET.SubElement(datacite, "datacite:identifier", {"identifierType": "URI"})
        datacite_identifier.text = identifier

        return_openaire_record(datacite, row)

    return to_pretty_xml(root)




""" LIST METADATA FORMAT """


def list_metadata_formats(args):
    root = create_base_response("ListMetadataFormats")
    list_formats = SubElement(root, f"{{{OAI_NS}}}ListMetadataFormats")

    format_el = SubElement(list_formats, f"{{{OAI_NS}}}metadataFormat")
    SubElement(format_el, f"{{{OAI_NS}}}metadataPrefix").text = OAI_OPENAIRE_PREFIX
    SubElement(format_el, f"{{{OAI_NS}}}schema").text = OPENAIRE_SCHEMA_LOCATION
    SubElement(format_el, f"{{{OAI_NS}}}metadataNamespace").text = OPENAIRE_NS

    return to_pretty_xml(root)


def return_openaire_record(record, row):
    for atlas_field, openaire_field in ATLAS_TO_OPENAIRE.items():
        if atlas_field in row:
            if openaire_field == 'datacite:title':
                titles_element = ET.SubElement(record, DATACITE_ET + 'titles')
                add_multiple_nested_elements(titles_element, openaire_field, row, atlas_field)
            elif openaire_field == 'dc:description' or openaire_field == 'dc:language' or openaire_field == 'oaire:file':
                value = row[atlas_field]["value"]
                for part in value.split("||"):
                    part = part.strip()
                    if part:
                        element = ET.SubElement(record, openaire_field)
                        element.text = part
            # # CREATORS and CONTRIBUTORS
            elif openaire_field == 'datacite:creator' or openaire_field == 'datacite:contributor':
                element = ET.SubElement(record, NESTED_ELEMENTS_MAP.get(openaire_field))
                set_agent(row[atlas_field]["value"], element, openaire_field)
            elif openaire_field == 'dc:publisher':
                set_publisher(row[atlas_field]["value"], record)
            elif openaire_field == 'oaire:resourceType':
                element = ET.SubElement(record, openaire_field)
                uri_rt = row[atlas_field]["value"]
                ret = RESOURCE_TYPE_DICT.get(uri_rt)
                rt_general = ret[0]
                value = ret[1]
                coar_url = ret[2]
                element.set("resourceTypeGeneral", rt_general)
                element.set("uri", coar_url)
                element.text = value
            elif openaire_field == 'datacite:subject':
                element = ET.SubElement(record, NESTED_ELEMENTS_MAP.get(openaire_field))
                subject = row[atlas_field]["value"]
                for part in subject.split("||"):
                    part = part.strip()
                    if part:
                        token = part.rsplit("/", 1)[-1]
                        subject_element = ET.SubElement(element, openaire_field)
                        subject_element.text = token
            elif openaire_field == 'datacite:alternateIdentifier':
                element = ET.SubElement(record, NESTED_ELEMENTS_MAP.get(openaire_field))
                url = row[atlas_field]["value"]
                for part in url.split("||"):
                    part = part.strip()
                    if part:
                        identifier_element = ET.SubElement(element, openaire_field,
                                                           {'alternateIdentifierType': 'URL'})
                        identifier_element.text = part
            elif openaire_field == 'oaire:fundingReference':
                element = ET.SubElement(record,  NESTED_ELEMENTS_MAP.get(openaire_field))
                projects = row[atlas_field]["value"]
                for project_id in projects.split("||"):
                    project_id = project_id.strip()
                    if project_id:
                        set_project(project_id, element, openaire_field)

            elif openaire_field == 'datacite:rights':
                access_rights = ET.SubElement(record, openaire_field)
                uri_access = row[atlas_field]["value"]
                access_rights.set("rightsURI", uri_access)
                access = RIGHTS_DICT.get(uri_access)
                access_rights.text = access
            elif openaire_field == 'oaire:licenseCondition':
                element = ET.SubElement(record, openaire_field)
                uri = row[atlas_field]["value"]
                element.text = get_label(uri)
            else:
                pass
                element = ET.SubElement(record, openaire_field)
                element.text = row[atlas_field]["value"]
    return record


# parent: parent element (e.g. datacite:titles node)
# field: name of the field to nest (e.g. datacite:title)
# row: data
# atlas_field: row field with the value to put in the nested field
def add_multiple_nested_elements(parent, field, row, atlas_field):
    value = row[atlas_field]["value"]
    for part in value.split("||"):
        part = part.strip()
        if part:
            nested_element = ET.SubElement(parent, field)
            nested_element.text = part
