from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
import chromedriver_autoinstaller
import logging
from urllib.parse import urlparse
import re
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Automatically install the appropriate ChromeDriver
chromedriver_autoinstaller.install()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://first-link-delta.vercel.app").split(",")
CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

# App configurations
app.config.update({
    "ENV": os.getenv("FLASK_ENV", "production"),
    "SECRET_KEY": os.getenv("SECRET_KEY", "default_secret_key"),
    "MAX_ITERATIONS": int(os.getenv("MAX_ITERATIONS", 30)),
    "PHILOSOPHY_URL": "https://en.wikipedia.org/wiki/Philosophy",
    "SELENIUM_WAIT_TIME": 10,
})
# Updated predefined_paths with steps count for each path
predefined_paths = {
    # Physics Path
    "https://en.wikipedia.org/wiki/Physics": {
        "path": [
            "https://en.wikipedia.org/wiki/Scientific",
            "https://en.wikipedia.org/wiki/Scientific_method",
            "https://en.wikipedia.org/wiki/Empirical_evidence",
            "https://en.wikipedia.org/wiki/Evidence",
            "https://en.wikipedia.org/wiki/Proposition",
            "https://en.wikipedia.org/wiki/Philosophy_of_language",
            "https://en.wikipedia.org/wiki/Language"
        ],
        "steps": 7  # Number of steps in the path
    },

    # Language Path
    "https://en.wikipedia.org/wiki/Language": {
        "path": [
            "https://en.wikipedia.org/wiki/Communication",
            "https://en.wikipedia.org/wiki/Information",
            "https://en.wikipedia.org/wiki/Abstraction",
            "https://en.wikipedia.org/wiki/Rule_of_inference",
            "https://en.wikipedia.org/wiki/Logic",
            "https://en.wikipedia.org/wiki/Logical_reasoning",
            "https://en.wikipedia.org/wiki/Mind",
            "https://en.wikipedia.org/wiki/Thought",
            "https://en.wikipedia.org/wiki/Cognition",
            "https://en.wikipedia.org/wiki/Action_(philosophy)",
            "https://en.wikipedia.org/wiki/Philosophy"
        ],
        "steps": 10
    },

    # Psychology Path
    "https://en.wikipedia.org/wiki/Psychology": {
        "path": [
            "https://en.wikipedia.org/wiki/Mind",
            "https://en.wikipedia.org/wiki/Thought",
            "https://en.wikipedia.org/wiki/Cognition",
            "https://en.wikipedia.org/wiki/Action_(philosophy)",
            "https://en.wikipedia.org/wiki/Philosophy"
        ],
        "steps": 5
    },

    # Sports Path
    "https://en.wikipedia.org/wiki/Sport": {
        "path": [
            "https://en.wikipedia.org/wiki/Physical_activity",
            "https://en.wikipedia.org/wiki/Skeletal_muscle",
            "https://en.wikipedia.org/wiki/Vertebrate",
            "https://en.wikipedia.org/wiki/Deuterostome",
            "https://en.wikipedia.org/wiki/Bilateria",
            "https://en.wikipedia.org/wiki/Clade",
            "https://en.wikipedia.org/wiki/Phylogenetics",
            "https://en.wikipedia.org/wiki/Biology"
        ],
        "steps": 8
    },

    # Biology Path
    "https://en.wikipedia.org/wiki/Biology": {
        "path": [
            "https://en.wikipedia.org/wiki/Life",
            "https://en.wikipedia.org/wiki/Matter",
            "https://en.wikipedia.org/wiki/Classical_physics",
            "https://en.wikipedia.org/wiki/Physics"
        ],
        "steps": 4
    },

    # History Path
    "https://en.wikipedia.org/wiki/History": {
        "path": [
            "https://en.wikipedia.org/wiki/Ancient_Greek",
            "https://en.wikipedia.org/wiki/Greek_language",
            "https://en.wikipedia.org/wiki/Ancient_Greek"
        ],
        "steps": 3
    },

    # Chemistry Path
    "https://en.wikipedia.org/wiki/Chemistry": {
        "path": [
            "https://en.wikipedia.org/wiki/Matter",
            "https://en.wikipedia.org/wiki/Classical_physics",
            "https://en.wikipedia.org/wiki/Physics"
        ],
        "steps": 3
    },

    # Politics Path
    "https://en.wikipedia.org/wiki/Politics": {
        "path": [
            "https://en.wikipedia.org/wiki/Decision-making",
            "https://en.wikipedia.org/wiki/Psychology"
        ],
        "steps": 2
    },

    # India Path
    "https://en.wikipedia.org/wiki/India": {
        "path": [
            "https://en.wikipedia.org/wiki/South_Asia",
            "https://en.wikipedia.org/wiki/Subregion#Asia",
            "https://en.wikipedia.org/wiki/Region",
            "https://en.wikipedia.org/wiki/Geography",
            "https://en.wikipedia.org/wiki/Earth",
            "https://en.wikipedia.org/wiki/Planet",
            "https://en.wikipedia.org/wiki/Hydrostatic_equilibrium",
            "https://en.wikipedia.org/wiki/Fluid_mechanics",
            "https://en.wikipedia.org/wiki/Physics"
        ],
        "steps": 9
    },

    # Philosophy Path
    "https://en.wikipedia.org/wiki/Philosophy": {
        "path": [
            "https://en.wikipedia.org/wiki/Existence",
            "https://en.wikipedia.org/wiki/Reality",
            "https://en.wikipedia.org/wiki/Universe",
            "https://en.wikipedia.org/wiki/Space",
            "https://en.wikipedia.org/wiki/Three-dimensional_space",
            "https://en.wikipedia.org/wiki/Geometry",
            "https://en.wikipedia.org/wiki/Mathematics",
            "https://en.wikipedia.org/wiki/Theory",
            "https://en.wikipedia.org/wiki/Reason",
            "https://en.wikipedia.org/wiki/Consciousness",
            "https://en.wikipedia.org/wiki/Awareness",
            "https://en.wikipedia.org/wiki/Philosophy"
        ],
        "steps": 12
    }
}

# Traverse Wikipedia pages
def traverse_wikipedia(start_url, max_iterations):
    driver = setup_driver()
    visited_urls = set()
    results = {"path": [], "steps": 0, "last_link": None}

    # Check if starting from Philosophy and return the predefined Philosophy path directly
    if start_url == "https://en.wikipedia.org/wiki/Philosophy":
        results.update({
            "path": predefined_paths[start_url]["path"],
            "steps": predefined_paths[start_url]["steps"],
            "last_link": predefined_paths[start_url]["path"][-1]
        })
        logging.info(f"Starting from Philosophy: Returning predefined path with {predefined_paths[start_url]['steps']} steps.")
        return results

    try:
        current_url = start_url
        logging.info(f"Starting traversal from: {current_url}")

        for step in range(max_iterations):
            # Check if current URL matches a predefined path
            if current_url in predefined_paths:
                predefined_path = predefined_paths[current_url]
                
                # Avoid adding the same URL if it's already in the visited path
                for url in predefined_path["path"]:
                    if url not in visited_urls:
                        visited_urls.add(url)
                        results["path"].append(url)
                        results["steps"] += 1
                        logging.info(f"Step {results['steps']}: Added predefined URL: {url}")
                        current_url = url  # Move to the next URL in the predefined path
                    if current_url == "https://en.wikipedia.org/wiki/Philosophy":
                        results.update({
                            "steps": results["steps"],
                            "last_link": current_url
                        })
                        logging.info(f"Reached Philosophy URL: {current_url}")
                        return results
                continue

            if current_url in visited_urls:
                return {**results, "error": f"Traversal ended in a loop at: {current_url}"}

            visited_urls.add(current_url)
            results["path"].append(current_url)
            logging.info(f"Step {results['steps'] + 1}: Visiting URL: {current_url}")

            if current_url == app.config["PHILOSOPHY_URL"]:
                results.update({"steps": results["steps"] + 1, "last_link": current_url})
                logging.info(f"Reached Philosophy URL: {current_url}")
                return results

            driver.get(current_url)
            next_url = find_first_anchor(driver)

            if not next_url:
                return {**results, "error": "No valid anchor link found in content."}

            current_url = next_url

        return {**results, "error": "Maximum iterations reached.", "visited_count": len(visited_urls)}
    except TimeoutException:
        return {**results, "error": "Timed out while waiting for page content."}
    except WebDriverException as e:
        logging.error(f"WebDriver exception: {e}")
        return {**results, "error": "Error occurred with WebDriver."}
    finally:
        driver.quit()

# Handle CORS preflight (OPTIONS request)
@app.before_request
def before_request():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = os.getenv("ALLOWED_ORIGINS", "https://first-link-delta.vercel.app")
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        return response

# Route to start traversal
@app.route("/start-traversal", methods=["POST"])
def start_traversal():
    data = request.get_json()
    start_url = data.get("start_url", app.config["PHILOSOPHY_URL"])

    if not is_valid_wikipedia_url(start_url):
        return jsonify({"error": "Invalid Wikipedia URL"}), 400

    result = traverse_wikipedia(start_url, app.config["MAX_ITERATIONS"])
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
