import logging
import os
import re
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

    logging.info(f"Received start_url from frontend: {start_url}")

    if not is_valid_wikipedia_url(start_url):
        logging.warning(f"Rejected start_url by validator: {start_url}")
        return jsonify({"error": "Invalid Wikipedia URL", "error_type": "invalid_url"}), 400

    result = traverse_wikipedia(start_url)
    status = 400 if "error" in result else 200
    return jsonify(result), status

def is_valid_wikipedia_url(url: str) -> bool:
    pattern = r"^https?://en\.wikipedia\.org/wiki/[^\s#]+$"
    is_valid = re.match(pattern, url.strip()) is not None
    logging.debug(f"Validating URL: {url.strip()} -> {is_valid}")
    return is_valid


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "Backend is running"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    debug_mode = Config.ENV == "development"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)