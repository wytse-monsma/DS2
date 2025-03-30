
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
import rdflib
import os
import sys

# Setup SPARQL endpoint
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)
sparql.addCustomHttpHeader("User-Agent", "Data Science/1.0")

name = "Wilminktheater"
city = "Enschede"
# Prepare the SPARQL query
query = f"""
    SELECT ?theater ?theaterLabel ?cityLabel WHERE {{
    ?theater wdt:P31/wdt:P279* wd:Q24354.   # instance of (subclass of) theatre building
    ?theater wdt:P17 wd:Q55.                # country is Netherlands
    
    ?theater rdfs:label ?name.                          # venue name in Dutch
    FILTER (CONTAINS(LCASE(?name), LCASE("{name}")))    # case-insensitive match
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 5
"""

sparql.setQuery(query)

# Run the query and parse the results
results = sparql.query().convert()["results"]["bindings"]

pprint(results)