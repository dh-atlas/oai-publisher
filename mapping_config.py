
mapping_config_openaire = {
    "identifier": {"json_field": "dataset", "xml_tag": "identifier", "attributes": {"identifierType": "URL"}},
    "creator": {"json_field": "creators", "xml_tag": "creators", "split": " || "},
    "title": {"json_field": "names", "xml_tag": "titles", "split": " || "},
    "publisher": {"json_field": "publishers", "xml_tag": "publishers", "split": " || "},
    "publicationYear": {"json_field": "datePublished", "xml_tag": "publicationYear", "year_only": True},
    "description": {"json_field": "descriptions", "xml_tag": "descriptions", "attributes": {"descriptionType": "Abstract"}, "split": " || "},
    "subject": {"json_field": "educationalUses", "xml_tag": "subjects", "split": " || "},
    "language": {"json_field": "languages", "xml_tag": "languages", "split": " || "},
    "resourceType": {"json_field": "type", "xml_tag": "resourceType", "attributes": {"resourceTypeGeneral": "Dataset"}}
}
