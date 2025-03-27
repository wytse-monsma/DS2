from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
import rdflib
import os
import sys

# Setup SPARQL endpoint
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)

# Load shows.ttl file
g = rdflib.Graph()
g.parse(os.path.join(os.path.dirname(sys.argv[0]), "shows.ttl"), format="turtle")

succes = 0

# Loop over all schema1:Persons in the graph, get wikidata equivalent and ad as owl:sameAs
for i, person in enumerate(g.subjects(rdflib.RDF.type, rdflib.URIRef("http://schema.org/Person")), start=1):
    # Extract the name of the person
    name = g.value(person, rdflib.URIRef("http://schema.org/name"))
    if name:
        print(name)

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
        print(results)
        
        if len(results) >= 1:
            succes += 1
            wikidata_id = results[0]["person"]["value"]
            print(f"Found Wikidata ID: {wikidata_id}")
            # Add owl:sameAs link to the graph
            g.add((person, rdflib.URIRef("http://www.w3.org/2002/07/owl#sameAs"), rdflib.URIRef(wikidata_id)))
        else:
            print(f"No Wikidata entry found for {name}")
        
        print(f"Total successful matches: {succes} from {i}")
        print()

# Save the updated graph to a new file
g.serialize(destination="shows_with_wikidata.ttl", format="turtle")

