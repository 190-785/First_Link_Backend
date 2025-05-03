import logging
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

from config import Config
from traversal import is_valid_wikipedia_url, traverse_wikipedia

# Configure root logger
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": Config.ALLOWED_ORIGINS}},
     supports_credentials=True)


@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        resp = make_response()
        origin = request.headers.get("Origin")
        allowed = Config.ALLOWED_ORIGINS[0]
        resp.headers["Access-Control-Allow-Origin"] = origin if origin in Config.ALLOWED_ORIGINS else allowed
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        return resp


@app.route("/start-traversal", methods=["POST"])
def start_traversal():
    data = request.get_json() or {}
    start_url = data.get("start_url", Config.PHILOSOPHY_URL)

    if not is_valid_wikipedia_url(start_url):
        return jsonify({"error": "Invalid Wikipedia URL"}), 400

    result = traverse_wikipedia(start_url)
    status = 400 if "error" in result and result.get("path") else 200
    return jsonify(result), status


if __name__ == "__main__":
    debug_mode = Config.ENV == "development"
    app.run(host="0.0.0.0", port=10000, debug=debug_mode)