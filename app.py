from werkzeug.middleware.proxy_fix import ProxyFix


from flask import Flask, send_from_directory, Response, make_response, render_template, request
from game import Puzzle, get_puzzle_data
import json

app = Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)


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
