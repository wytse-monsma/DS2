from flask import Flask, request, jsonify, render_template
import rdflib
import os
import sys

app = Flask(__name__)

# Load shows.ttl file
graph = rdflib.Graph()
graph.parse(os.path.join(os.path.dirname(sys.argv[0]), "enriched_shows.ttl"), format="turtle")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    sparql_query = data.get("query", "")
    try:
        result = graph.query(sparql_query)
        results_list = []
        for row in result:
            row_dict = {str(var): str(row[var]) for var in result.vars}
            results_list.append(row_dict)
        return jsonify({"status": "success", "results": results_list})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)