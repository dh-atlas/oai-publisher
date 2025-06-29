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

LIST_IDENTIFIERS_QUERY = """SELECT DISTINCT ?dataset
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
  (GROUP_CONCAT(DISTINCT ?publisherName; separator=" || ") AS ?publishers)
  (GROUP_CONCAT(DISTINCT ?inLanguage; separator=" || ") AS ?languages)
  (GROUP_CONCAT(DISTINCT ?educationalUse; separator=" || ") AS ?educationalUses)
  (GROUP_CONCAT(DISTINCT ?distribution; separator=" || ") AS ?distributions)
  (GROUP_CONCAT(DISTINCT ?url; separator=" || ") AS ?urls)
  (GROUP_CONCAT(DISTINCT ?producer; separator=" || ") AS ?producers)
  ?additionalType
  ?datePublished
  ?conditionsOfAccess
  ?license
WHERE {
  ?dataset <http://schema.org/name> ?name ; rdf:type <https://schema.org/Dataset> .
  OPTIONAL {{ ?dataset <http://schema.org/description> ?description . }}
  OPTIONAL {{ ?dataset <http://schema.org/creator> ?creator . }}
  OPTIONAL {{ ?dataset <http://schema.org/publisher> ?publisher . ?publisher <http://schema.org/name> ?publisherName . }}
  OPTIONAL {{ ?dataset <http://schema.org/additionalType> ?additionalType . }}
  OPTIONAL {{ ?dataset <http://schema.org/datePublished> ?datePublished . }}
  OPTIONAL {{ ?dataset <http://schema.org/educationalUse> ?educationalUse . }}
  OPTIONAL {{ ?dataset <http://schema.org/distribution> ?distribution . }}
  OPTIONAL {{ ?dataset <http://schema.org/url> ?url . }}
  OPTIONAL {{ ?dataset <http://schema.org/conditionsOfAccess> ?conditionsOfAccess . }}
  OPTIONAL {{ ?dataset <http://schema.org/contributor> ?contributor . }}
  OPTIONAL {{ ?dataset <http://schema.org/inLanguage> ?inLanguage . }}
  OPTIONAL {{ ?dataset <http://schema.org/producer> ?producer . }}
  OPTIONAL {{ ?dataset <http://schema.org/license> ?license . }}
  }
GROUP BY ?additionalType ?datePublished ?conditionsOfAccess ?dataset ?license
"""

GET_RECORD_QUERY = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?dataset
       (GROUP_CONCAT(DISTINCT ?name; separator=" || ") AS ?names)
       (GROUP_CONCAT(DISTINCT ?description; separator=" || ") AS ?descriptions)
       (GROUP_CONCAT(DISTINCT ?creator; separator=" || ") AS ?creators)
       (GROUP_CONCAT(DISTINCT ?contributor; separator=" || ") AS ?contributors)
       (GROUP_CONCAT(DISTINCT ?publisherName; separator=" || ") AS ?publishers)
       (GROUP_CONCAT(DISTINCT ?inLanguage; separator=" || ") AS ?languages)
       (GROUP_CONCAT(DISTINCT ?educationalUse; separator=" || ") AS ?educationalUses)
       (GROUP_CONCAT(DISTINCT ?distribution; separator=" || ") AS ?distributions)
       (GROUP_CONCAT(DISTINCT ?url; separator=" || ") AS ?urls)
       (GROUP_CONCAT(DISTINCT ?producer; separator=" || ") AS ?producers)
       ?additionalType
       ?datePublished
       ?conditionsOfAccess
       ?license
WHERE {
  BIND(<{identifier}> AS ?dataset)
  ?dataset <http://schema.org/name> ?name ; rdf:type <https://schema.org/Dataset> .
  OPTIONAL {{ ?dataset <http://schema.org/description> ?description . }}
  OPTIONAL {{ ?dataset <http://schema.org/creator> ?creator . }}
  OPTIONAL {{ ?dataset <http://schema.org/publisher> ?publisher . ?publisher <http://schema.org/name> ?publisherName . }}
  OPTIONAL {{ ?dataset <http://schema.org/additionalType> ?additionalType . }}
  OPTIONAL {{ ?dataset <http://schema.org/datePublished> ?datePublished . }}
  OPTIONAL {{ ?dataset <http://schema.org/educationalUse> ?educationalUse . }}
  OPTIONAL {{ ?dataset <http://schema.org/distribution> ?distribution . }}
  OPTIONAL {{ ?dataset <http://schema.org/url> ?url . }}
  OPTIONAL {{ ?dataset <http://schema.org/conditionsOfAccess> ?conditionsOfAccess . }}
  OPTIONAL {{ ?dataset <http://schema.org/contributor> ?contributor . }}
  OPTIONAL {{ ?dataset <http://schema.org/inLanguage> ?inLanguage . }}
  OPTIONAL {{ ?dataset <http://schema.org/producer> ?producer . }}
  OPTIONAL {{ ?dataset <http://schema.org/license> ?license . }}
}
GROUP BY ?additionalType ?datePublished ?conditionsOfAccess ?dataset ?license
"""


GET_AGENT_QUERY = """
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT *
WHERE {
   BIND(<{identifier}> AS ?agent)
         ?agent schema:name ?name .
        OPTIONAL {
         ?agent schema:affiliation ?aff .
        ?aff schema:name ?affName .
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
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT *
WHERE {
   BIND(<{identifier}> AS ?project)
	?project schema:name ?name .
	?project schema:funder ?funder .
  	?funder schema:name ?funderName .
	OPTIONAL {
		?project schema:identifier ?id .
	}
 }

"""
