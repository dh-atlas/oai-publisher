import json
import xml.etree.ElementTree as ET

import mapping_config
from mapping_config import mapping_config_openaire

def json_to_datacite(json_response, mapping_config):
    root = ET.Element("resource", xmlns="http://datacite.org/schema/kernel-4")

    for binding in json_response["results"]["bindings"]:
        for key, config in mapping_config.items():
            json_field = config["json_field"]
            xml_tag = config["xml_tag"]
            attributes = config.get("attributes", {})
            split = config.get("split")
            year_only = config.get("year_only", False)

            if json_field in binding:
                value = binding[json_field]["value"]

                if split:
                    values = value.split(split)
                else:
                    values = [value]

                for val in values:
                    element = ET.SubElement(root, xml_tag, **attributes)
                    if year_only:
                        val = val.split("-")[0]
                    element.text = val

    return ET.tostring(root, encoding="unicode")

# Sample JSON response
json_response = {
    "head" : {
        "vars" : [
            "dataset",
            "type",
            "names",
            "descriptions",
            "creators",
            "contributors",
            "publishers",
            "languages",
            "educationalUses",
            "distributions",
            "urls",
            "producers",
            "additionalType",
            "datePublished",
            "conditionsOfAccess"
        ]
    },
    "results" : {
        "bindings" : [
            {
                "dataset" : {
                    "type" : "uri",
                    "value" : "https://w3id.org/dh-atlas/1728943937-3007112"
                },
                "type" : {
                    "type" : "uri",
                    "value" : "https://schema.org/Dataset"
                },
                "names" : {
                    "type" : "literal",
                    "value" : "Zeri Photo Archive RDF Dataset"
                },
                "descriptions" : {
                    "type" : "literal",
                    "value" : "The Zeri Photo Archive RDF dataset represents a considerable subset of data already available at Zeri Catalog web site and discoverable through the Europeana Portal, mostly regarding works of Modern Art (15th-16th centuries): about 19.000 works of art and more than 30.000 photographs depicting such works are accurately described by means of like 10 million of RDF triples."
                },
                "creators" : {
                    "type" : "literal",
                    "value" : "https://w3id.org/dh-atlas/1728943969-854 || https://w3id.org/dh-atlas/1728943988-693 || https://w3id.org/dh-atlas/1728944010-053 || https://w3id.org/dh-atlas/1728944026-501 || https://w3id.org/dh-atlas/1728944045-966"
                },
                "contributors" : {
                    "type" : "literal",
                    "value" : ""
                },
                "publishers" : {
                    "type" : "literal",
                    "value" : "https://w3id.org/dh-atlas/1728944565-1916842"
                },
                "languages" : {
                    "type" : "literal",
                    "value" : "http://publications.europa.eu/resource/authority/language/ENG || http://publications.europa.eu/resource/authority/language/ITA"
                },
                "educationalUses" : {
                    "type" : "literal",
                    "value" : "https://vocabs.dariah.eu/tadirah/cataloging || https://vocabs.dariah.eu/tadirah/knowledgeDiscovery || https://vocabs.dariah.eu/tadirah/knowledgeExtraction"
                },
                "distributions" : {
                    "type" : "literal",
                    "value" : "https://amsacta.unibo.it/id/eprint/5497/2/dump-complete-13-1-2017.zip"
                },
                "urls" : {
                    "type" : "literal",
                    "value" : "https://w3id.org/zericatalog"
                },
                "producers" : {
                    "type" : "literal",
                    "value" : "https://w3id.org/dh-atlas/1728984604-1499374"
                },
                "additionalType" : {
                    "type" : "uri",
                    "value" : "https://w3id.org/dh-atlas/LinkedOpenData"
                },
                "datePublished" : {
                    "datatype" : "http://www.w3.org/2001/XMLSchema#date",
                    "type" : "literal",
                    "value" : "2016-05-20"
                },
                "conditionsOfAccess" : {
                    "type" : "uri",
                    "value" : "http://purl.org/coar/access_right/c_abf2"
                }
            }
        ]
    }
}

# Convert JSON to DataCite XML
xml_output = json_to_datacite(json_response, mapping_config.mapping_config_openaire)

# Save the XML output to a file
with open("datacite_record.xml", "w") as xml_file:
    xml_file.write(xml_output)

print("DataCite XML record has been saved to datacite_record.xml")

