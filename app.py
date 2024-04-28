from flask import Flask, send_from_directory, Response, make_response, render_template, request
from game import Puzzle, get_puzzle_data
import json

app = Flask(__name__)

@app.route("/random")
def random_puzzle():
    p = Puzzle.gen_random()
    result = p.to_json()
    return Response(result, mimetype='application/json')

@app.route("/<path>")
def main(path):
    response = make_response(send_from_directory(".", path))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/")
def index():
    return render_template("start.html")


@app.route("/get_puzzle")
def get_puzzle():
    hu_only = request.args.get("hu_only") == "on"
    rand = request.args.get("random") == "on"
    try:
        errors = request.args.get("errors")
        errors = int(errors)
    except ValueError:
        print(f"Got wrong value {errors=}")
        errors=0

    try:
        progress = request.args.get("progress")
        progress = int(progress)
    except ValueError:
        print(f"Got wrong value {progress=}")
        progress = 0


    if rand:
        tax_id = None
    else:
        try:
            tax_id = int(request.args.get("tax_id"))
        except ValueError:
            return "Wrong tax_id"

    data = get_puzzle_data(hu_only=hu_only, rand=rand, tax_id=tax_id, errors=errors, progress=progress)

    return render_template("puzzle.html", **data)
