from flask import Flask, jsonify
from src.core import build_payload_dict

app = Flask(__name__)
app.json.sort_keys = False 

@app.route("/data", methods=["GET"])
def data():
    return jsonify(build_payload_dict())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7774)
