# key = ATALS type = COAR type (OpenAIRE)
RESOURCE_TYPE_DICT ={
    'https://schema.org/Dataset': ['dataset','dataset'],
    'https://w3id.org/dh-atlas/DigitalScholarlyEdition': ['dataset','encoded data'],
    'https://w3id.org/dh-atlas/LinkedOpenData':['dataset','dataset'],
    'https://w3id.org/dh-atlas/Ontology': ['dataset','knowledge organization system'],
    'https://w3id.org/dh-atlas/Software': ['software','software'],
    'https://w3id.org/dh-atlas/TextCollection': ['dataset','collection'],
    'https://w3id.org/dh-atlas/3DDigitalTwin':['dataset','dataset'], 
    'https://w3id.org/dh-atlas/LanguageModel': ['software','software']
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
    'license' : 'license',
    'uri' : 'uri'
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
    'oaire:licenseCondition' : ['license'],
    'oai_datacite:alternateIdentifier': ['url']
}

