# oai-publisher

**OAI-PMH server and client in Flask for publishing RDF metadata according to the OpenAIRE model.**

This project implements a Flask application that exposes an OAI-PMH (Open Archives Initiative Protocol for Metadata Harvesting) interface, mapping SPARQL queries to a Blazegraph endpoint containing RDF files from the **DH-ATLAS** project. The returned metadata complies with the [**oai-datacite** profile](https://openaire-guidelines-for-literature-repository-managers.readthedocs.io/en/v4.0.0/use_of_oai_pmh.html) required by OpenAIRE.

## Features

- OAI-PMH server with support for the following verbs:
  - `Identify`
  - `ListIdentifiers`
  - `ListRecords` (with and without `metadataPrefix`)
  - `GetRecord` (with and without `metadataPrefix`)
  - `ListMetadataFormats`

- OAI-PMH client for testing and harvesting.
- RDF → OpenAIRE mapping via CSV/XLSX files.
- Output compliant with the `oai-datacite` profile.

## Repository structure

```
oai-publisher/
├── datacite_record.xml              # XML template for oai-datacite records
├── dicts.py                         # Support dictionaries for mapping
├── handlers.py                      # OAI-PMH verb handling
├── licences.ttl                     # RDF file with licenses
├── map-atlas-openaire-resproduct.csv  # CSV mapping ATLAS → OpenAIRE
├── mapping ATLAS-OpenAIRE.xlsx     # XLSX mapping ATLAS → OpenAIRE
├── mapping.py                      # Data transformation logic
├── mapping_config.py               # Mapping configuration
├── namespaces.py                   # RDF namespace definitions
├── oai-server.py                   # Flask server entry point
├── raw_handlers.py                 # Raw handling of OAI-PMH verbs
├── response.py                     # XML response construction
├── sparql.py                       # SPARQL queries to Blazegraph
```
