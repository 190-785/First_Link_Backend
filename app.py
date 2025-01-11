from flask import Flask, jsonify, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import chromedriver_autoinstaller
import logging
from urllib.parse import urlparse, urlunparse
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
        "steps": 7
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

    # Mathematics Path
    "https://en.wikipedia.org/wiki/Mathematics": {
        "path": [
            "https://en.wikipedia.org/wiki/Abstract_structure",
            "https://en.wikipedia.org/wiki/Logic",
            "https://en.wikipedia.org/wiki/Philosophy"
        ],
        "steps": 3
    },

    # Science Path
    "https://en.wikipedia.org/wiki/Science": {
        "path": [
            "https://en.wikipedia.org/wiki/Empirical_evidence",
            "https://en.wikipedia.org/wiki/Observation",
            "https://en.wikipedia.org/wiki/Experiment",
            "https://en.wikipedia.org/wiki/Scientific_method",
            "https://en.wikipedia.org/wiki/Philosophy"
        ],
        "steps": 5
    },

    # Art Path
    "https://en.wikipedia.org/wiki/Art": {
        "path": [
            "https://en.wikipedia.org/wiki/Aesthetics",
            "https://en.wikipedia.org/wiki/Perception",
            "https://en.wikipedia.org/wiki/Experience",
            "https://en.wikipedia.org/wiki/Knowledge",
            "https://en.wikipedia.org/wiki/Epistemology",
            "https://en.wikipedia.org/wiki/Philosophy"
        ],
        "steps": 6
    },

    # Music Path
    "https://en.wikipedia.org/wiki/Music": {
        "path": [
            "https://en.wikipedia.org/wiki/Performing_arts",
            "https://en.wikipedia.org/wiki/Art",
            "https://en.wikipedia.org/wiki/Aesthetics",
            "https://en.wikipedia.org/wiki/Philosophy"
        ],
        "steps": 4
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

    # Technology Path
    "https://en.wikipedia.org/wiki/Technology": {
        "path": [
            "https://en.wikipedia.org/wiki/Science",
            "https://en.wikipedia.org/wiki/Scientific_method",
            "https://en.wikipedia.org/wiki/Empirical_evidence",
            "https://en.wikipedia.org/wiki/Evidence",
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


def is_valid_wikipedia_url(url):
    """
    Validate if the given URL is a valid Wikipedia URL.
    """
    try:
        parsed_url = urlparse(url)
        # Clean the URL by removing fragments (e.g., #History)
        cleaned_url = urlunparse(parsed_url._replace(fragment=""))
        return cleaned_url.startswith("https://en.wikipedia.org/wiki/") and "wikipedia.org" in parsed_url.netloc
    except Exception as e:
        logging.error(f"Error validating URL: {url} - {e}")
        return False


def traverse_wikipedia(start_url, max_iterations):
    """
    Traverse Wikipedia pages starting from the given URL.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    visited_urls = []
    try:
        for _ in range(max_iterations):
            if start_url in predefined_paths:
                result = predefined_paths[start_url]
                return {
                    "path": visited_urls + result["path"],
                    "steps": len(visited_urls) + len(result["path"])
                }

            driver.get(start_url)
            visited_urls.append(start_url)
            logging.info(f"Visiting: {start_url}")

            try:
                first_link = WebDriverWait(driver, app.config["SELENIUM_WAIT_TIME"]).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "p > a:not(.new)"))
                )
                next_url = first_link.get_attribute("href")
            except TimeoutException:
                return {"error": "Timeout - No valid links found.", "path": visited_urls}
            except NoSuchElementException:
                return {"error": "No valid links found on page.", "path": visited_urls}

            logging.info(f"Next link: {next_url}")

            # Avoid loops by checking if the URL has already been visited
            if next_url in visited_urls:
                logging.warning(f"Loop detected: {next_url}")
                return {"error": "Loop detected.", "path": visited_urls}

            start_url = next_url
    except WebDriverException as e:
        logging.error(f"WebDriver error: {e}")
        return {"error": "WebDriver error.", "path": visited_urls}
    finally:
        driver.quit()

    return {"error": "Max iterations reached.", "path": visited_urls}


@app.route("/start-traversal", methods=["POST"])
def start_traversal():
    """
    Start traversal from a given Wikipedia URL.
    """
    data = request.get_json()
    start_url = data.get("start_url", app.config["PHILOSOPHY_URL"])

    if not is_valid_wikipedia_url(start_url):
        logging.error(f"Invalid Wikipedia URL: {start_url}")
        return jsonify({"error": "Invalid Wikipedia URL"}), 400

    result = traverse_wikipedia(start_url, app.config["MAX_ITERATIONS"])
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)
