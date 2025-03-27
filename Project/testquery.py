
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
import rdflib
import os
import sys

# Setup SPARQL endpoint
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)

name = "Hannah Mae"
# Prepare the SPARQL query
query = f"""
    SELECT DISTINCT ?person (COUNT(*) AS ?popularity) WHERE {{
    ?person wdt:P31 wd:Q5.            # instance of human
    ?person ?label "{name}"@nl.
    ?person ?p ?o.           # any property
    {{?person wdt:P106 ?occupation.     # has occupation
    ?occupation wdt:P279* wd:Q713200.}}  # occupation is actor or subclass of performing artist
    UNION
    {{?person wdt:P106 ?occupation.     # has occupation
    ?occupation wdt:P279* wd:Q639669.}}  # occupation is actor or subclass of musician
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    GROUP BY ?person
    ORDER BY DESC(?popularity)
    LIMIT 5
"""

sparql.setQuery(query)

# Run the query and parse the results
results = sparql.query().convert()["results"]["bindings"]

pprint(results)