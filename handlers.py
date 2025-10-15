import mapping
import mapping_config
from sparql import LIST_IDENTIFIERS_QUERY, LIST_RECORDS_QUERY, GET_RECORD_QUERY, GET_AGENT_QUERY
from response import create_base_response, to_pretty_xml, to_json_response, handle_oai_error, OAI_PMH_Error
from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import SubElement
from dicts import SPARQL_STD_DICT, DATACITE_TO_STD_DICT, RIGHTS_DICT, RESOURCE_TYPE_DICT
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

from rdflib import Graph, URIRef
from rdflib.namespace import SKOS

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
    ET.SubElement(identify, f"{{{OAI_NS}}}repositoryName").text = OAI_SPARQL_BE
    ET.SubElement(identify, f"{{{OAI_NS}}}baseURL").text = BASE_URL
    ET.SubElement(identify, f"{{{OAI_NS}}}protocolVersion").text = "2.0"
    admins = ET.SubElement(identify, f"{{{OAI_NS}}}admins")
    ET.SubElement(admins, f"{{{OAI_NS}}}adminEmail").text = "giorgia.rubin@cnr.it | g.rubin@studenti.unipi.it" 
    ET.SubElement(admins, f"{{{OAI_NS}}}adminEmail").text = "alessia.bardi@cnr.it"
    ET.SubElement(admins, f"{{{OAI_NS}}}adminEmail").text = "riccardo.delgratta@cnr.it"
    ET.SubElement(admins, f"{{{OAI_NS}}}adminEmail").text = "angelo.delgrosso@cnr.it"
    ET.SubElement(admins, f"{{{OAI_NS}}}adminEmail").text = "marilena.daquino@unibo.it"
    ET.SubElement(identify, f"{{{OAI_NS}}}earliestDatestamp").text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    ET.SubElement(identify, f"{{{OAI_NS}}}deletedRecord").text = "no"
    ET.SubElement(identify, f"{{{OAI_NS}}}granularity").text = "YYYY-MM-DDThh:mm:ssZ" #
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
        ET.SubElement(h, f"{{{OAI_NS}}}datestamp").text = datetime.utcnow().isoformat() + "Z"
    return to_pretty_xml(root)



""" LIST RECORDS """

def handler_list_records(metadata_prefix):
    if metadata_prefix is None:  # no metadataPrexif to test SPARQL results with default namespace
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
        ET.SubElement(header_elem, f"{{{OAI_NS}}}datestamp").text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

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
    if metadata_prefix == OAI_DATACITE_PF:
        return list_records_oai_datacite()

'''
datacite record formats the native output of blazegraph SPARQL endpoint so that:
1. it uses the correct namespaces for datacite
2. it expands multiple values separated by ||
'''

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

        datacite = return_formatted_datacite(datacite, row)        
                    
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
            element = ET.SubElement(parent_node, DATACITE_ET + element_name)
            name = ET.SubElement(element, DATACITE_ET + element_name + 'Name')
            name.text = row['name']["value"]
            if "affName" in row:
                aff = ET.SubElement(element, DATACITE_ET + 'affiliation')
                aff.text = row['affName']["value"]
            if "orcid" in row:
                orcid = ET.SubElement(element, DATACITE_ET + 'nameIdentifier', nameIdentifierScheme='ORCID', schemeURI='http://orcid.org')
                orcid.text = row['orcid']["value"]
            if "wiki" in row:
                wiki = ET.SubElement(element, DATACITE_ET + 'nameIdentifier', nameIdentifierScheme='WIKI', schemeURI='http://www.wikidata.org')
                wiki.text = row['wiki']["value"]


""" SET PROJECT """                                                                                    

def set_project(projects: str, parent_node: SubElement, element_name: str):
    project_list = projects.split('||')
    for project in project_list:
        # Query data from SPARQL
        query = GET_AGENT_QUERY.replace('{identifier}', project.strip())
        sparql.setQuery(query)
        results = sparql.query().convert()
        for row in results["results"]["bindings"]:
            element = ET.SubElement(parent_node, OAIRE_ET + element_name)
            elementName = ET.SubElement(element, OAIRE_ET + 'funderName')
            elementName.text = row['name']["value"]


""" SET PUBLISHER """

def set_publisher(agents: str, parent_node: SubElement, element_name: str):
    agent_list = agents.split('||')
    for agent in agent_list:
        # Query data from SPARQL
        query = GET_AGENT_QUERY.replace('{identifier}', agent.strip())
        sparql.setQuery(query)
        results = sparql.query().convert()
        for row in results["results"]["bindings"]:
            element = ET.SubElement(parent_node, DATACITE_ET + element_name)
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
    if metadata_prefix == OAI_DATACITE_PF:
        return get_record_oai_datacite(identifier)

def get_record_oai_datacite(identifier):
    
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

        datacite = return_formatted_datacite(datacite, row)        
                    
    #Count for log
    #print(f"Founded: {num_lic} licenses ({sanity_list_lic}) and {num_access} accesseRights")
    return to_pretty_xml(root)


def get_record_oai_datacite_old(identifier):
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
    #record.append(metadata)
    record.append(mapping.json_to_datacite(results, mapping_config.mapping_config_openaire))

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



def return_formatted_datacite(datacite, row):

    # Count for log to be completed
    num_lic=0
    num_access=0
    sanity_list_lic=[]
    sanity_list_ac=[]

    # Process all fields according to mapping dictionaries
    for source_field, target_fields in DATACITE_TO_STD_DICT.items():
        for target_field in target_fields:
            # Get the corresponding SPARQL field name
            sparql_field = SPARQL_STD_DICT.get(target_field)
            if sparql_field and sparql_field in row:

                # Create element with appropriate namespace

                #TITLE                                                    
                if target_field == 'name':
                    names_element = ET.SubElement(datacite, DATACITE_ET + 'titles')
                    original_text = row[sparql_field]["value"]
                    for part in original_text.split("||"):
                        part = part.strip()
                        if part:
                            name_element = ET.SubElement(names_element, DATACITE_ET + 'title')
                            name_element.text = part                            

                #DESCRIPTION
                elif target_field == 'description':
                    descriptions_element = ET.SubElement(datacite, DC_ET + 'descriptions')
                    original_text = row[sparql_field]["value"]
                    for part in original_text.split("||"):
                        part = part.strip()
                        if part:
                            description_element = ET.SubElement(descriptions_element, DC_ET + 'description')
                            description_element.text = part

                #CREATOR
                elif source_field == OAI_DATACITE_PF + ':creator':
                    element = ET.SubElement(datacite, DATACITE_ET + 'creators')
                    set_agent(row[sparql_field]["value"], element, 'creator')

                #CONTRIBUTOR
                elif source_field == OAI_DATACITE_PF + ':contributor':
                    element = ET.SubElement(datacite, DATACITE_ET + 'contributors')                 #attrubute type: if orcid-> type= "researcher" / if not-> type= "other"
                    set_agent(row[sparql_field]["value"], element, 'contributor')

                #PUBLISHER
                elif source_field == OAI_DC_PF + ':publisher':
                    element = ET.SubElement(datacite, DATACITE_ET + 'publishers')
                    set_publisher(row[sparql_field]["value"], element, 'publisher')

                #RESEARCH TYPE
                elif target_field == 'additionalType':
                    element = ET.SubElement(datacite, OAIRE_ET + 'resourceType')
                    uri_rt = row[sparql_field]["value"]
                    rt_general= "Not Found"
                    value= "Not Found"
                    ret = RESOURCE_TYPE_DICT.get(uri_rt)
                    rt_general=ret[0]
                    value=ret[1]
                    element.set("resourceTypeGeneral",rt_general)
                    element.set("uri",uri_rt)
                    element.text = value

                #DATE as it is

                #LANGUAGE
                elif target_field == 'inLanguage':
                    element = ET.SubElement(datacite, DC_ET + 'languages')
                    lang = row[sparql_field]["value"]
                    for part in lang.split("||"):
                        part = part.strip()
                        if part:
                            lang_code = part[-3:]
                            lang_element = ET.SubElement(element, DC_ET + "language")
                            lang_element.text = lang_code    
                                    
                #SUBJECT
                elif target_field == 'educationalUse':
                    element = ET.SubElement(datacite, DATACITE_ET + 'subjects')
                    subject = row[sparql_field]["value"]
                    for part in subject.split("||"):
                        part = part.strip()
                        if part:
                            token = part.rsplit("/", 1)[-1]
                            subject_element = ET.SubElement(element, DATACITE_ET + "subject")
                            subject_element.text = token

                #FILE
                elif target_field == 'distribution':
                    files_element = ET.SubElement(datacite, OAIRE_ET + 'files')
                    original_text = row[sparql_field]["value"]
                    for part in original_text.split("||"):
                        part = part.strip()
                        if part:
                            file_element = ET.SubElement(files_element, OAIRE_ET + 'file')
                            file_element.text = part

                #ALTERNATIVE IDENTIFIER
                elif target_field == 'url':
                    element = ET.SubElement(datacite, DATACITE_ET + 'alternativeIdentifiers')  
                    url = row[sparql_field]["value"]
                    for part in url.split("||"):
                        part = part.strip()
                        if part:
                            identifier_element = ET.SubElement(element, DATACITE_ET + 'alternativeIdentifier', {'alternateIdentifierType': 'URL'})
                            identifier_element.text = part

                #FUNDING REFERENCE
                elif source_field == OAI_OAIRE_PF + ':fundingReference':
                    element = ET.SubElement(datacite, OAIRE_ET + 'fundingReferences')
                    set_project(row[sparql_field]["value"], element, 'fundingReference')

                #ACCESS RIGHT
                elif target_field == 'accessRights':
                    num_access=num_access+1
                    #sanity_list_ac.append(identifier)
                    access_rights = ET.SubElement(datacite, DATACITE_ET + 'rights')
                    rights = ET.SubElement(access_rights, DATACITE_ET + 'right') 
                    uri_access = row[sparql_field]["value"]
                    rights.set("rightsURI",uri_access)
                    access= "Not Found"
                    access = RIGHTS_DICT.get(uri_access)
                    rights.text = access

                #LICENSE
                elif sparql_field == 'license':
                    num_lic=num_lic+1
                    #sanity_list_lic.append(identifier)
                    element = ET.SubElement(datacite, OAIRE_ET + 'licenseCondition')
                    uri = row[sparql_field]["value"]
                    lic_name = get_label(uri)
                    element.text = lic_name



                elif source_field.startswith(OAI_DATACITE_PF):
                    field_name = source_field.split(':')[1]
                    element = ET.SubElement(datacite, DATACITE_ET + field_name)
                    # Set the value from SPARQL results
                    element.text = row[sparql_field]["value"]
                elif source_field.startswith(OAI_DC_PF):
                    field_name = source_field.split(':')[1]
                    element = ET.SubElement(datacite, DC_ET + field_name)
                    # Set the value from SPARQL results
                    element.text = row[sparql_field]["value"]
                elif source_field.startswith(OAI_OAIRE_PF):
                    field_name = source_field.split(':')[1]
                    element = ET.SubElement(datacite, OAIRE_ET + field_name)
                    # Set the value from SPARQL results
                    element.text = row[sparql_field]["value"]
                    
                else:
                    pass
    return datacite