# key = ATLAS type = COAR type (OpenAIRE)
RESOURCE_TYPE_DICT = {
    'https://schema.org/Dataset': ['dataset', 'dataset', 'http://purl.org/coar/resource_type/c_ddb1'],
    'https://w3id.org/dh-atlas/DigitalScholarlyEdition': ['dataset', 'encoded data', 'http://purl.org/coar/resource_type/AM6W-6QAW'],
    'https://w3id.org/dh-atlas/LinkedOpenData': ['dataset', 'dataset', 'http://purl.org/coar/resource_type/c_ddb1'],
    'https://w3id.org/dh-atlas/Ontology': ['dataset', 'knowledge organization system', 'http://purl.org/coar/resource_type/GSZA-Y7V7'],
    'https://w3id.org/dh-atlas/Software': ['software', 'software', 'http://purl.org/coar/resource_type/c_5ce6'],
    'https://w3id.org/dh-atlas/TextCollection': ['dataset', 'collection', 'http://purl.org/coar/resource_type/RMP5-3GQ6'],
    'https://w3id.org/dh-atlas/3DDigitalTwin': ['dataset', 'dataset', 'http://purl.org/coar/resource_type/c_ddb1'],
    'https://w3id.org/dh-atlas/LanguageModel': ['software', 'software', 'http://purl.org/coar/resource_type/c_5ce6']
}

# key = rightURI = COAR label
RIGHTS_DICT = {
    'http://purl.org/coar/access_right/c_abf2': 'open access',
    'http://purl.org/coar/access_right/c_f1cf': 'embargoed access',
    'http://purl.org/coar/access_right/c_16ec': 'restricted access',
    'http://purl.org/coar/access_right/c_14cb': 'metadata only access'
}

# key = element name value = the sparql variable. Ex name to names
SPARQL_STD_DICT = {
    'dataset': 'dataset',
    'name': 'names',
    'description': 'descriptions',
    'creator': 'creators',
    'contributor': 'contributors',
    'publisher': 'publishers',
    'inLanguage': 'languages',
    'educationalUse': 'educationalUses',
    'distribution': 'distributions',
    'url': 'urls',
    'producer': 'producers',
    'additionalType': 'additionalType',
    'datePublished': 'datePublished',
    'accessRights': 'accessRights',
    'license': 'license',
    'uri': 'uri'
}

# key = oai_datacite element name value = std dict element name. Ex title=name
DATACITE_TO_STD_DICT = {
    'oai_datacite:identifier': ['uri'],
    'oai_datacite:title': ['name'],
    'oai_dc:description': ['description'],
    'oai_datacite:creator': ['creator'],
    'oai_datacite:contributor': ['contributor'],
    'oai_dc:publisher': ['publisher'],
    'oaire:resourceType': ['additionalType'],
    'oai_datacite:date': ['datePublished'],
    'oai_dc:language': ['inLanguage'],
    'oai_datacite:subject': ['educationalUse'],
    'oaire:file': ['distribution'],
    'oaire:fundingReference': ['producer'],
    'oai_datacite:rights': ['accessRights'],
    'oaire:licenseCondition': ['license'],
    'oai_datacite:alternateIdentifier': ['url']
}

# Map ATLAS fields to OpenAIRE fields
# Key = atlas field as returned by the SPARQL query (sparql.py)
# Value = OpenAIRE field. Nested structure (e.g. <datacite:creators><datacite:creator>) is handled by the python code.
ATLAS_TO_OPENAIRE = {
    'names': 'datacite:title',
    'descriptions': 'dc:description',
    'creators': 'datacite:creator',
    'contributors': 'datacite:contributor',
    'publishers': 'dc:publisher',
    'languages': 'dc:language',
    'educationalUses': 'datacite:subject',
    'distributions': 'oaire:file',
    'urls': 'datacite:alternateIdentifier',
    'producers': 'oaire:fundingReference',
    'additionalType': 'oaire:resourceType',
    'datePublished': 'datacite:date',
    'accessRights': 'datacite:rights',
    'license': 'oaire:licenseCondition'
}

# Map nested element to their parent
# key = child
# value = parent
NESTED_ELEMENTS_MAP = {
    'datacite:title': 'datacite:titles',
    'datacite:creator': 'datacite:creators',
    'datacite:contributor': 'datacite:contributors',
    'datacite:alternateIdentifier': 'datacite:alternateIdentifiers',
    'oaire:fundingReference': 'oaire:fundingReferences'
}
