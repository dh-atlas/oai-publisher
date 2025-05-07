#key=element name value=the sparql variable. Ex name to names
SPARQL_STD_DICT={
"dataset":"dataset",
"name":"names",
"description":"descriptions",
"creator":"creators",
"contributor":"contributors",
"publisher":"publishers",
"language":"languages",
"educationalUse":"educationalUses",
"distribution":"distributions",
"url":"urls",
"producer":"producers",
"additionalType":"additionalType",
"datePublished":"datePublished",
"conditionsOfAccess":"conditionsOfAccess"
}

#key = oai_datacite element name value=std dict element name. Ex title=name
DATACITE_TO_STD_DICT = {
    'oai_datacite:title': ['name'],
    'oai_dc:description': ['description'],
    'oai_datacite:creator': ['creator'],
    'oai_datacite:contributor': ['contributor'],
    'oai_dc:publisher': ['publisher'],
    'additionalType': ['oaire:resourceType'],
    'oai_datacite:date': ['datePublished'],
    'oai_dc:language': ['language'],
    'oai_datacite:subject': ['educationalUse'],
    'oaire:file': ['distribution', 'url'],
    'oaire:fundingReference': ['producer'],
    'oai_datacite:rights': ['conditionsOfAccess']
}

