import os
import sys
import json
from urllib.parse import quote
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import FOAF, DC, DCTERMS, XSD
import re

# Sample data (replace with actual JSON parsing if loading from file)
data = json.load(open(os.path.join(os.path.dirname(sys.argv[0]), "shows.json")))

# Define namespaces
SCHEMA = Namespace("http://schema.org/")
EX = Namespace("http://example.org/")
WD = Namespace("http://www.wikidata.org/entity/")

# Create graph
g = Graph()
g.bind("schema", SCHEMA)
g.bind("ex", EX)
g.bind("wd", WD)

for idx, show in enumerate(data):
    show_uri = URIRef(EX[f"show/show{idx+1}"])
    g.add((show_uri, RDF.type, SCHEMA.Event))
    g.add((show_uri, SCHEMA.name, Literal(show['title'])))
    g.add((show_uri, SCHEMA.description, Literal(show['short_description_dutch'], lang="nl")))
    g.add((show_uri, SCHEMA.startDate, Literal(show['date'], datatype=XSD.dateTime)))
    g.add((show_uri, SCHEMA.price, Literal(show['price_eur'], datatype=XSD.float)))

    # Add theater as a separate Place
    
    match = re.search(r"^(.*?)\s*\(([^)]+)\)", show['location'])
    if match:
        theater_name = match.group(1).strip()
        city = match.group(2).strip()
    else:
        theater_name = show['location'].strip()
        city = None
    
    theater_id = theater_name.replace(" ", "_")
    theater_uri = URIRef(EX[f"venue/{theater_id}"])
    g.add((theater_uri, RDF.type, SCHEMA.Place))
    g.add((theater_uri, SCHEMA.name, Literal(theater_name)))
    
    if city:
        g.add((theater_uri, SCHEMA.addressLocality, Literal(city)))

    # Link show to theater
    g.add((show_uri, SCHEMA.location, theater_uri))

    # Add performers
    for artist in show['artists']:
        artist_uri = URIRef(EX[f"artist/{quote(artist.replace(' ', '_'))}"])
        g.add((artist_uri, RDF.type, SCHEMA.Person))
        g.add((artist_uri, SCHEMA.name, Literal(artist)))
        g.add((show_uri, SCHEMA.performer, artist_uri))

    # Add genres as literals (or link to Wikidata if known)
    for genre in show['genre']:
        g.add((show_uri, SCHEMA.genre, Literal(genre)))

# Save the graph to a ttl file
output_file = os.path.join(os.path.dirname(sys.argv[0]), "shows.ttl")
