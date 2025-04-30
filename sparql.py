# sparql.py

LIST_IDENTIFIERS_QUERY_1 = """
PREFIX schema: <https://schema.org/>
PREFIX fabio: <http://purl.org/spar/fabio/>
SELECT ?id ?type
WHERE {
    ?id a ?type .
    FILTER (?type = schema:Dataset || 
            ?type = fabio:ComputerProgram || 
            ?type = fabio:Anthology || 
            ?type = fabio:MetadataDocument || 
            ?type = fabio:OntologyDocument || 
            ?type = fabio:DataFile)
}
"""

LIST_IDENTIFIERS_QUERY= """SELECT DISTINCT ?dataset
WHERE {
  
  ?dataset <http://schema.org/name> ?name ; rdf:type <https://schema.org/Dataset> .
}
"""

LIST_RECORDS_QUERY = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 

SELECT ?dataset
  (GROUP_CONCAT(DISTINCT ?name; separator=" || ") AS ?names)
  (GROUP_CONCAT(DISTINCT ?description; separator=" || ") AS ?descriptions)
  (GROUP_CONCAT(DISTINCT ?creator; separator=" || ") AS ?creators)
  (GROUP_CONCAT(DISTINCT ?contributor; separator=" || ") AS ?contributors)
  (GROUP_CONCAT(DISTINCT ?publisher; separator=" || ") AS ?publishers)
  (GROUP_CONCAT(DISTINCT ?inLanguage; separator=" || ") AS ?languages)
  (GROUP_CONCAT(DISTINCT ?educationalUse; separator=" || ") AS ?educationalUses)
  (GROUP_CONCAT(DISTINCT ?distribution; separator=" || ") AS ?distributions)
  (GROUP_CONCAT(DISTINCT ?url; separator=" || ") AS ?urls)
  (GROUP_CONCAT(DISTINCT ?producer; separator=" || ") AS ?producers)
  ?additionalType
  ?datePublished
  ?conditionsOfAccess
WHERE {
  ?dataset <http://schema.org/name> ?name ; rdf:type <https://schema.org/Dataset> .
  OPTIONAL { ?dataset <http://schema.org/description> ?description . }
  OPTIONAL { ?dataset <http://schema.org/creator> ?creator . }
  OPTIONAL { ?dataset <http://schema.org/publisher> ?publisher . }
  OPTIONAL { ?dataset <http://schema.org/additionalType> ?additionalType . }
  OPTIONAL { ?dataset <http://schema.org/datePublished> ?datePublished . }
  OPTIONAL { ?dataset <http://schema.org/educationalUse> ?educationalUse . }
  OPTIONAL { ?dataset <http://schema.org/distribution> ?distribution . }
  OPTIONAL { ?dataset <http://schema.org/url> ?url . }
  OPTIONAL { ?dataset <http://schema.org/conditionsOfAccess> ?conditionsOfAccess . }
  OPTIONAL { ?dataset <http://schema.org/contributor> ?contributor . }
  OPTIONAL { ?dataset <http://schema.org/inLanguage> ?inLanguage . }
  OPTIONAL { ?dataset <http://schema.org/producer> ?producer . }
}
GROUP BY ?additionalType ?datePublished ?conditionsOfAccess ?dataset
"""


GET_RECORD_QUERY = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?dataset
       (GROUP_CONCAT(DISTINCT ?name; separator=" || ") AS ?names)
       (GROUP_CONCAT(DISTINCT ?description; separator=" || ") AS ?descriptions)
       (GROUP_CONCAT(DISTINCT ?creator; separator=" || ") AS ?creators)
       (GROUP_CONCAT(DISTINCT ?contributor; separator=" || ") AS ?contributors)
       (GROUP_CONCAT(DISTINCT ?publisher; separator=" || ") AS ?publishers)
       (GROUP_CONCAT(DISTINCT ?inLanguage; separator=" || ") AS ?languages)
       (GROUP_CONCAT(DISTINCT ?educationalUse; separator=" || ") AS ?educationalUses)
       (GROUP_CONCAT(DISTINCT ?distribution; separator=" || ") AS ?distributions)
       (GROUP_CONCAT(DISTINCT ?url; separator=" || ") AS ?urls)
       (GROUP_CONCAT(DISTINCT ?producer; separator=" || ") AS ?producers)
       ?additionalType
       ?datePublished
       ?conditionsOfAccess
WHERE {{
  BIND(<{identifier}> AS ?dataset)
  ?dataset <http://schema.org/name> ?name ; rdf:type <https://schema.org/Dataset> .
  OPTIONAL {{ ?dataset <http://schema.org/description> ?description . }}
  OPTIONAL {{ ?dataset <http://schema.org/creator> ?creator . }}
  OPTIONAL {{ ?dataset <http://schema.org/publisher> ?publisher . }}
  OPTIONAL {{ ?dataset <http://schema.org/additionalType> ?additionalType . }}
  OPTIONAL {{ ?dataset <http://schema.org/datePublished> ?datePublished . }}
  OPTIONAL {{ ?dataset <http://schema.org/educationalUse> ?educationalUse . }}
  OPTIONAL {{ ?dataset <http://schema.org/distribution> ?distribution . }}
  OPTIONAL {{ ?dataset <http://schema.org/url> ?url . }}
  OPTIONAL {{ ?dataset <http://schema.org/conditionsOfAccess> ?conditionsOfAccess . }}
  OPTIONAL {{ ?dataset <http://schema.org/contributor> ?contributor . }}
  OPTIONAL {{ ?dataset <http://schema.org/inLanguage> ?inLanguage . }}
  OPTIONAL {{ ?dataset <http://schema.org/producer> ?producer . }}
}}
GROUP BY ?additionalType ?datePublished ?conditionsOfAccess ?dataset
"""

