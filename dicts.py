# key= ATALS type = COAR type (OpenAIRE)
RESOURCE_TYPE_DICT ={
    'http://schema.org/Dataset': '<oaire:resourceType resourceTypeGeneral="dataset" uri="http://purl.org/coar/resource_type/c_ddb1">dataset</oaire:resourceType>',
    'http://www.w3id.org/dh-atlas/DigitalScholarlyEdition': '<oaire:resourceType resourceTypeGeneral="dataset" uri="http://purl.org/coar/resource_type/AM6W-6QAW">encoded data</oaire:resourceType>',
    'https://w3id.org/dh-atlas/LinkedOpenData': '<oaire:resourceType resourceTypeGeneral="dataset" uri="http://purl.org/coar/resource_type/c_ddb1">dataset</oaire:resourceType>',
    'http://www.w3id.org/dh-atlas/Ontology': '<oaire:resourceType resourceTypeGeneral="dataset" uri="http://purl.org/coar/resource_type/GSZA-Y7V7">knowledge organization system</oaire:resourceType>',
    'http://www.w3id.org/dh-atlas/Software': '<oaire:resourceType resourceTypeGeneral="software" uri="http://purl.org/coar/resource_type/c_5ce6">software</oaire:resourceType>',
    'http://www.w3id.org/dh-atlas/TextCollection': '<oaire:resourceType resourceTypeGeneral="dataset" uri="http://purl.org/coar/resource_type/RMP5-3GQ6">collection</oaire:resourceType>'
}

# key=element name value=the sparql variable. Ex name to names
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
    'conditionsOfAccess': 'conditionsOfAccess'
}

# key = oai_datacite element name value=std dict element name. Ex title=name
DATACITE_TO_STD_DICT = {
    'oai_datacite:title': ['name'],
    'oai_dc:description': ['description'],
    'oai_datacite:creator': ['creator'],
    'oai_datacite:contributor': ['contributor'],
    'oai_dc:publisher': ['publisher'],
    'oaire:resourceType': ['additionalType'], 
    'oai_datacite:date': ['datePublished'],
    'oai_dc:language': ['inLanguage'],
    'oai_datacite:subject': ['educationalUse'],
    'oaire:file': ['distribution', 'url'],
    'oaire:fundingReference': ['producer'],
    'oai_datacite:rights': ['conditionsOfAccess']
}

