
mapping_config_openaire = {
"identifier": {"json_field": "dataset", "xml_tag": "identifier", "attributes": {"identifierType": "URL"}},
"creators": {"json_field": "creators", "xml_tag": "creators", "split": " || "},
"title": {"json_field": "names", "xml_tag": "titles"},
"publisher": {"json_field": "publishers", "xml_tag": "publisher"},
"publicationYear": {"json_field": "datePublished", "xml_tag": "publicationYear", "year_only": True},
"description": {"json_field": "descriptions", "xml_tag": "descriptions", "attributes": {"descriptionType": "Abstract"}},
"subjects": {"json_field": "educationalUses", "xml_tag": "subjects", "split": " || "},
"language": {"json_field": "languages", "xml_tag": "language"},
"resourceType": {"json_field": "type", "xml_tag": "resourceType", "attributes": {"resourceTypeGeneral": "Dataset"}}
}
