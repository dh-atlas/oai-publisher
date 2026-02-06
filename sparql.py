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

LIST_IDENTIFIERS_QUERY = """SELECT DISTINCT ?dataset
WHERE {
  
  ?dataset <https://schema.org/name> ?name ; rdf:type <https://schema.org/Dataset> .
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
  ?accessRights
  ?license
WHERE {
  ?dataset <https://schema.org/name> ?name ; rdf:type <https://schema.org/Dataset> .
  OPTIONAL { ?dataset <https://schema.org/description> ?description . }
  OPTIONAL { ?dataset <https://schema.org/creator> ?creator . }
  OPTIONAL { ?dataset <https://schema.org/publisher> ?publisher . }
  OPTIONAL { ?dataset <https://schema.org/additionalType> ?additionalType . }
  OPTIONAL { ?dataset <https://schema.org/datePublished> ?datePublished . }
  OPTIONAL { ?dataset <https://schema.org/educationalUse> ?educationalUse . }
  OPTIONAL { ?dataset <https://schema.org/distribution> ?distribution . }
  OPTIONAL { ?dataset <https://schema.org/url> ?url . }
  OPTIONAL { ?dataset <http://purl.org/dc/terms/accessRights> ?accessRights . }
  OPTIONAL { ?dataset <https://schema.org/contributor> ?contributor . }
  OPTIONAL { ?dataset <https://schema.org/inLanguage> ?inLanguage . }
  OPTIONAL { ?dataset <https://schema.org/producer> ?producer . }
  OPTIONAL { ?dataset <https://schema.org/license> ?license . }
}
GROUP BY ?additionalType ?datePublished ?accessRights ?dataset ?license
"""

GET_RECORD_QUERY = """
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
  ?accessRights
  ?license
WHERE {{
  BIND(<{identifier}> AS ?dataset)
  ?dataset <https://schema.org/name> ?name ; rdf:type <https://schema.org/Dataset> .
  OPTIONAL {{ ?dataset <https://schema.org/description> ?description . }}
  OPTIONAL {{ ?dataset <https://schema.org/creator> ?creator . }}
  OPTIONAL {{ ?dataset <https://schema.org/publisher> ?publisher . ?publisher <https://schema.org/name> ?publisherName . }}  
  OPTIONAL {{ ?dataset <https://schema.org/additionalType> ?additionalType . }}
  OPTIONAL {{ ?dataset <https://schema.org/datePublished> ?datePublished . }}
  OPTIONAL {{ ?dataset <https://schema.org/educationalUse> ?educationalUse . }}
  OPTIONAL {{ ?dataset <https://schema.org/distribution> ?distribution . }}
  OPTIONAL {{ ?dataset <https://schema.org/url> ?url . }}
  OPTIONAL {{ ?dataset <http://purl.org/dc/terms/accessRights> ?accessRights . }}
  OPTIONAL {{ ?dataset <https://schema.org/contributor> ?contributor . }}
  OPTIONAL {{ ?dataset <https://schema.org/inLanguage> ?inLanguage . }}
  OPTIONAL {{ ?dataset <https://schema.org/producer> ?producer . }}
  OPTIONAL {{ ?dataset <https://schema.org/license> ?license . }}
}}
GROUP BY ?additionalType ?datePublished ?accessRights ?dataset ?license
"""

GET_AGENT_QUERY = """
PREFIX schema: <https://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT *
WHERE {
   BIND(<{identifier}> AS ?agent)
         ?agent schema:name ?name .
        OPTIONAL {
         ?agent schema:affiliation ?affiliation .
         ?affiliation schema:name ?affName .
        }
        OPTIONAL {
           ?agent schema:identifier ?orcid .
            FILTER (strstarts(str(?orcid), 'https://orcid.org'))
        }
        OPTIONAL {
             ?agent schema:sameAs ?wiki .
            FILTER (strstarts(str(?wiki), 'http://www.wikidata.org'))
        }            
   }
"""

GET_PROJECT_QUERY = """
PREFIX schema: <https://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?title  (GROUP_CONCAT(DISTINCT ?fundername; separator=" || ") AS ?fundernames)
WHERE {
   BIND(<{identifier}> AS ?project)
   ?project schema:name ?title .
   ?project schema:funder ?f .
   ?f schema:name ?fundername
         
   }
GROUP BY ?title
"""


