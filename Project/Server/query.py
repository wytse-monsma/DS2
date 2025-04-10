# Run a query using /query endpoint

import requests
import json

# Define the URL of the Flask server
url = "http://localhost:5000/query"

sparql_queryI = """
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT ?venue_name (COUNT(?award) as ?awards) (COUNT(?artist) as ?artists) (COUNT(DISTINCT ?artist) as ?distinct_artists) WHERE {

        ?artist a schema1:Person .
        ?artist owl:sameAs ?wikidata_artist .

        SERVICE <https://query.wikidata.org/sparql> {
            OPTIONAL { ?wikidata_artist wdt:P166 ?award . }
        }

        ?show a schema1:Event .
        ?show schema1:performer ?artist .
        ?show schema1:location ?venue .
        ?venue schema1:name ?venue_name .
    }
    GROUP BY ?venue
    ORDER BY DESC(?awards)
"""

sparql_queryII = """
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT ?school_name (COUNT(?award) as ?awards) WHERE {

        ?artist a schema1:Person .
        ?artist owl:sameAs ?wikidata_artist .

        SERVICE <https://query.wikidata.org/sparql> {
            ?wikidata_artist wdt:P166 ?award .
            ?wikidata_artist wdt:P69 ?school .
            ?school rdfs:label ?school_name .
            FILTER (lang(?school_name) = "nl")
        }
    }
    GROUP BY ?school_name
    ORDER BY DESC(?awards)
"""

sparql_queryIII = """
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT ?province_name (COUNT(?show) as ?shows) WHERE {

        ?artist a schema1:Person .
        ?artist owl:sameAs ?wikidata_artist .

        SERVICE <https://query.wikidata.org/sparql> {
            ?wikidata_artist wdt:P19 ?birth_city .
            ?birth_city wdt:P131 ?birth_province .
            ?birth_province wdt:P31 wd:Q134390 .
            ?birth_province rdfs:label ?province_name .
            FILTER (lang(?province_name) = "nl")
        }

        ?show a schema1:Event .
        ?show schema1:performer ?artist .
        ?show schema1:genre "Cabaret" .
    }
    GROUP BY ?birth_province
    ORDER BY DESC(?shows)
"""

sparql_query = """
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT ?province_name (COUNT(?show) as ?shows) WHERE {

        ?venue a schema1:Place .
        ?venue owl:sameAs ?wikidata_venue .

        SERVICE <https://query.wikidata.org/sparql> {
            ?wikidata_venue wdt:P131 ?city .
            ?city wdt:P131 ?province .
            ?province rdfs:label ?province_name .
            FILTER (lang(?province_name) = "nl")
        }

        ?show a schema1:Event .
        ?show schema1:location ?venue .
        ?show schema1:genre "Cabaret" .
    }
    GROUP BY ?province
    ORDER BY DESC(?shows)
"""


# Prepare the payload
payload = {
    "query": sparql_query
}

# Send the POST request
response = requests.post(url, json=payload)

# Check the response status code
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    if data["status"] == "success":
        results = data["results"]
        for result in results:
            print(result)
        print("Length of results:", len(results))

        # Write results to a file
        with open("results.json", "w") as f:
            json.dump(results, f)
    else:
        print("Error:", data["message"])
else:
    print("Failed to connect to the server. Status code:", response.status_code)
    print("Response:", response.text)