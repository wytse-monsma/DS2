import rdflib
import os
import sys

import WikiDataLinker

# Load shows.ttl file
g = rdflib.Graph()
g.parse(os.path.join(os.path.dirname(sys.argv[0]), "shows.ttl"), format="turtle")

# Enrich actors the graph with WikiData links
g = WikiDataLinker.enrich_actor(g)

# Enrich venues the graph with WikiData links
g = WikiDataLinker.enrich_venue(g)

# Save the enriched graph to a ttl file
output_file = os.path.join(os.path.dirname(sys.argv[0]), "enriched_shows.ttl")
g.serialize(destination=output_file, format="turtle")