from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
import rdflib
import time

def enrich_actor(g):
    # Setup SPARQL endpoint
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)
    sparql.addCustomHttpHeader("User-Agent", "Data Science/1.0")

    succes = 0

    actors = list(g.subjects(rdflib.RDF.type, rdflib.URIRef("http://schema.org/Person")))

    # Loop over all schema1:Persons in the graph, get wikidata equivalent and ad as owl:sameAs
    for i, person in enumerate(actors, start=1):
        while True:
            # Extract the name of the person
            name = g.value(person, rdflib.URIRef("http://schema.org/name"))
            print(name)

            # Prepare the SPARQL query
            query = f"""
                SELECT DISTINCT ?person (COUNT(*) AS ?popularity) WHERE {{
                ?person wdt:P31 wd:Q5.            # instance of human
                ?person ?label "{name}"@nl.
                ?person ?p ?o.           # any property
                {{?person wdt:P106/wdt:P279* wd:Q713200. }}  # occupation is performing artist or subclass of it 
                UNION
                {{?person wdt:P106/wdt:P279* wd:Q639669. }}     # occupation is musician or subclass of it
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                }}
                GROUP BY ?person
                ORDER BY DESC(?popularity)
                LIMIT 5
            """
            
            sparql.setQuery(query)

            try:
                response = sparql.query()
                break
            except Exception as e:
                print(f"Error running query: {e}")
                print(response.info())
                time.sleep(5)
                continue

        # Run the query and parse the results
        results = response.convert()["results"]["bindings"]
        print(results)
        
        if len(results) >= 1:
            succes += 1
            wikidata_id = results[0]["person"]["value"]
            print(f"Found Wikidata ID: {wikidata_id}")
            # Add owl:sameAs link to the graph
            g.add((person, rdflib.URIRef("http://www.w3.org/2002/07/owl#sameAs"), rdflib.URIRef(wikidata_id)))
        else:
            print(f"No Wikidata entry found for {name}")
        
        print(f"Total successful matches: {succes} from {i} from total of {len(actors)}")
        print()

    return g


def enrich_venue(g):
    # Setup SPARQL endpoint
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)
    sparql.addCustomHttpHeader("User-Agent", "Data Science/1.0")

    succes = 0

    venues = list(g.subjects(rdflib.RDF.type, rdflib.URIRef("http://schema.org/Place")))

    # Loop over all schema1:Persons in the graph, get wikidata equivalent and ad as owl:sameAs
    for i, venue in enumerate(venues, start=1):
        while True:
            # Extract the name of the person
            name = g.value(venue, rdflib.URIRef("http://schema.org/name")).replace("Theater ", "").replace("Theater", "").strip()
            city = g.value(venue, rdflib.URIRef("http://schema.org/addressLocality"))

            print(name, city)

            if city:
                # Prepare the SPARQL query
                query = f"""
                    SELECT DISTINCT ?theater WHERE {{
                    ?city rdfs:label "{city}"@nl.                       # city name in Dutch
                    ?theater wdt:P131 ?city.                            # located in administrative region (e.g., city)
                    ?theater wdt:P17 wd:Q55.                            # country is Netherlands
                    ?theater wdt:P31/wdt:P279* wd:Q24354.               # instance of (subclass of) theatre building
                    
                    ?theater rdfs:label ?name.                          # venue name in Dutch
                    FILTER (CONTAINS(LCASE(?name), LCASE("{name}")))    # case-insensitive match
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                    }}
                    LIMIT 5
                """
            else:
                # Prepare the SPARQL query
                query = f"""
                    SELECT DISTINCT ?theater WHERE {{
                    ?theater wdt:P31/wdt:P279* wd:Q24354.   # instance of (subclass of) theatre building
                    ?theater wdt:P17 wd:Q55.                # country is Netherlands
                    
                    ?theater rdfs:label ?name.                          # venue name in Dutch
                    FILTER (CONTAINS(LCASE(?name), LCASE("{name}")))    # case-insensitive match
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                    }}
                    LIMIT 5
                """
            
            sparql.setQuery(query)

            try:
                response = sparql.query()
                break
            except Exception as e:
                print(f"Error running query: {e}")
                print(response.info())
                time.sleep(5)
                continue

        # Run the query and parse the results
        results = response.convert()["results"]["bindings"]
        print(results)
        
        if len(results) == 1:
            succes += 1
            wikidata_id = results[0]["theater"]["value"]
            print(f"Found Wikidata ID: {wikidata_id}")
            # Add owl:sameAs link to the graph
            g.add((venue, rdflib.URIRef("http://www.w3.org/2002/07/owl#sameAs"), rdflib.URIRef(wikidata_id)))
        elif len(results) > 1:
            print(f"Multiple Wikidata entries found for {name}:")
            for result in results:
                print(result["theater"]["value"])
        else:
            print(f"No Wikidata entry found for {name}")
        
        print(f"Total successful matches: {succes} from {i} from total of {len(venues)}")
        print()

    return g

