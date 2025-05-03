import logging
import os
import re
from flask import Flask, request, jsonify # Removed make_response as it's no longer needed without manual OPTIONS handler
from flask_cors import CORS

from config import Config
# Assuming traversal module has is_valid_wikipedia_url and traverse_wikipedia functions
from traversal import is_valid_wikipedia_url, traverse_wikipedia

# Configure root logger
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config.from_object(Config)

# Configure CORS using Flask-CORS. This handles OPTIONS requests automatically.
# Ensure Config.ALLOWED_ORIGINS is a list like ["https://first-link-delta.vercel.app"]
CORS(app, resources={r"/*": {"origins": Config.ALLOWED_ORIGINS}},
     supports_credentials=True)

# --- REMOVE THIS FUNCTION ---
# The Flask-CORS extension handles the OPTIONS preflight requests automatically.
# Having this manual handler is redundant and can cause conflicts.
# @app.before_request
# def handle_options():
#     if request.method == "OPTIONS":
#         resp = make_response()
#         origin = request.headers.get("Origin")
#         # This manual logic is usually not needed with Flask-CORS
#         allowed = Config.ALLOWED_ORIGINS[0]
#         resp.headers["Access-Control-Allow-Origin"] = origin if origin in Config.ALLOWED_ORIGINS else allowed
#         resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
#         resp.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
#         return resp
# --------------------------

@app.route("/start-traversal", methods=["POST"]) # Flask-CORS will handle the OPTIONS preflight for this route
def start_traversal():
    data = request.get_json() or {}
    start_url = data.get("start_url", Config.PHILOSOPHY_URL)

    logging.info(f"Received start_url from frontend: {start_url}")

    # Ensure these functions are correctly imported from your traversal module
    if not is_valid_wikipedia_url(start_url):
        logging.warning(f"Rejected start_url by validator: {start_url}")
        return jsonify({"error": "Invalid Wikipedia URL", "error_type": "invalid_url"}), 400

    # Call your actual traversal logic
    result = traverse_wikipedia(start_url)
    status = 400 if "error" in result else 200
    return jsonify(result), status


# Assuming this function is defined in traversal.py, ensure it is imported
# If it's defined here, keep it.
# def is_valid_wikipedia_url(url: str) -> bool:
#     pattern = r"^https?://en\.wikipedia\.org/wiki/[^\s#]+$"
#     is_valid = re.match(pattern, url.strip()) is not None
#     logging.debug(f"Validating URL: {url.strip()} -> {is_valid}")
#     return is_valid

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "Backend is running"})


if __name__ == "__main__":
    # Use the PORT environment variable provided by Railway
    port = int(os.environ.get("PORT", 10000))
    # Determine debug mode based on environment variable
    debug_mode = Config.ENV == "development" # Make sure Config.ENV is set appropriately in config.py
    # Ensure host is '0.0.0.0' for Railway to be accessible externally
    app.run(host="0.0.0.0", port=port, debug=debug_mode)

