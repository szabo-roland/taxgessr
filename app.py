from flask import Flask, send_from_directory, Response, make_response
from game import Puzzle
import json

app = Flask(__name__)

@app.route("/random")
def random_puzzle():
    p = Puzzle.gen_random()
    result = p.to_json()
    return Response(result, mimetype='application/json')

@app.route("/<path>")
def index(path):
    response = make_response(send_from_directory(".", path))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
