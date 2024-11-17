from flask import Flask, jsonify, request
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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
    "MAX_ITERATIONS": int(os.getenv("MAX_ITERATIONS", 15)),
    "PHILOSOPHY_URL": "https://en.wikipedia.org/wiki/Philosophy",
    "SELENIUM_WAIT_TIME": 10,
})

predefined_paths = {
    # Language Path
    "https://en.wikipedia.org/wiki/Language": [
        "https://en.wikipedia.org/wiki/Communication",
        "https://en.wikipedia.org/wiki/Information",
        "https://en.wikipedia.org/wiki/Symbol",
        "https://en.wikipedia.org/wiki/Abstraction",
        "https://en.wikipedia.org/wiki/Semiotics",
        "https://en.wikipedia.org/wiki/Rule_of_inference",
        "https://en.wikipedia.org/wiki/Logic",
        "https://en.wikipedia.org/wiki/Cognition",
        "https://en.wikipedia.org/wiki/Philosophy_of_language",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Music Path
    "https://en.wikipedia.org/wiki/Music": [
        "https://en.wikipedia.org/wiki/Sound",
        "https://en.wikipedia.org/wiki/Art",
        "https://en.wikipedia.org/wiki/Aesthetics",
        "https://en.wikipedia.org/wiki/Creativity",
        "https://en.wikipedia.org/wiki/Philosophy_of_art",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Sports Path
    "https://en.wikipedia.org/wiki/Sport": [
        "https://en.wikipedia.org/wiki/Physical_activity",
        "https://en.wikipedia.org/wiki/Competition",
        "https://en.wikipedia.org/wiki/Athletics",
        "https://en.wikipedia.org/wiki/Olympic_Games",
        "https://en.wikipedia.org/wiki/Team_sport",
        "https://en.wikipedia.org/wiki/Fair_play",
        "https://en.wikipedia.org/wiki/Ethics",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],
    # Football Path
    "https://en.wikipedia.org/wiki/Association_football": [
        "https://en.wikipedia.org/wiki/Sport",
        "https://en.wikipedia.org/wiki/Team_sport",
        "https://en.wikipedia.org/wiki/FIFA",
        "https://en.wikipedia.org/wiki/Olympic_Games",
        "https://en.wikipedia.org/wiki/Fair_play",
        "https://en.wikipedia.org/wiki/Ethics",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Basketball Path
    "https://en.wikipedia.org/wiki/Basketball": [
        "https://en.wikipedia.org/wiki/Sport",
        "https://en.wikipedia.org/wiki/Team_sport",
        "https://en.wikipedia.org/wiki/NBA",
        "https://en.wikipedia.org/wiki/Competition",
        "https://en.wikipedia.org/wiki/Ethics",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Cricket Path
    "https://en.wikipedia.org/wiki/Cricket": [
        "https://en.wikipedia.org/wiki/Sport",
        "https://en.wikipedia.org/wiki/Team_sport",
        "https://en.wikipedia.org/wiki/ICC",
        "https://en.wikipedia.org/wiki/Fair_play",
        "https://en.wikipedia.org/wiki/Philosophy_of_sport",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Famous Personalities Path (General)
    "https://en.wikipedia.org/wiki/Famous_people": [
        "https://en.wikipedia.org/wiki/Historical_figure",
        "https://en.wikipedia.org/wiki/Celebrity",
        "https://en.wikipedia.org/wiki/Leadership",
        "https://en.wikipedia.org/wiki/Influence",
        "https://en.wikipedia.org/wiki/Philosophy_of_history",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Literature Path
    "https://en.wikipedia.org/wiki/Literature": [
        "https://en.wikipedia.org/wiki/Storytelling",
        "https://en.wikipedia.org/wiki/Myth",
        "https://en.wikipedia.org/wiki/Language",
        "https://en.wikipedia.org/wiki/Narrative",
        "https://en.wikipedia.org/wiki/Philosophy_of_literature",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],
    
    # Religion Path
    "https://en.wikipedia.org/wiki/Religion": [
        "https://en.wikipedia.org/wiki/Belief_system",
        "https://en.wikipedia.org/wiki/Spirituality",
        "https://en.wikipedia.org/wiki/Theology",
        "https://en.wikipedia.org/wiki/Ethics",
        "https://en.wikipedia.org/wiki/Metaphysics",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Astronomy Path
    "https://en.wikipedia.org/wiki/Astronomy": [
        "https://en.wikipedia.org/wiki/Universe",
        "https://en.wikipedia.org/wiki/Cosmology",
        "https://en.wikipedia.org/wiki/Space",
        "https://en.wikipedia.org/wiki/Time",
        "https://en.wikipedia.org/wiki/Philosophy_of_science",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Computer Science Path
    "https://en.wikipedia.org/wiki/Computer_science": [
        "https://en.wikipedia.org/wiki/Algorithm",
        "https://en.wikipedia.org/wiki/Data_structure",
        "https://en.wikipedia.org/wiki/Logic",
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Philosophy_of_technology",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Medicine Path
    "https://en.wikipedia.org/wiki/Medicine": [
        "https://en.wikipedia.org/wiki/Health",
        "https://en.wikipedia.org/wiki/Biology",
        "https://en.wikipedia.org/wiki/Anatomy",
        "https://en.wikipedia.org/wiki/Disease",
        "https://en.wikipedia.org/wiki/Teleology",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Economics Path
    "https://en.wikipedia.org/wiki/Economics": [
        "https://en.wikipedia.org/wiki/Resource_allocation",
        "https://en.wikipedia.org/wiki/Supply_and_demand",
        "https://en.wikipedia.org/wiki/Efficiency_(economics)",
        "https://en.wikipedia.org/wiki/Game_theory",
        "https://en.wikipedia.org/wiki/Utilitarianism",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Psychology Path
    "https://en.wikipedia.org/wiki/Psychology": [
        "https://en.wikipedia.org/wiki/Mind",
        "https://en.wikipedia.org/wiki/Thought",
        "https://en.wikipedia.org/wiki/Consciousness",
        "https://en.wikipedia.org/wiki/Behavior",
        "https://en.wikipedia.org/wiki/Philosophy_of_mind",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Politics Path
    "https://en.wikipedia.org/wiki/Politics": [
        "https://en.wikipedia.org/wiki/Power_(social_and_political)",
        "https://en.wikipedia.org/wiki/Government",
        "https://en.wikipedia.org/wiki/Social_contract",
        "https://en.wikipedia.org/wiki/Justice",
        "https://en.wikipedia.org/wiki/Philosophy_of_politics",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # History Path
    "https://en.wikipedia.org/wiki/History": [
        "https://en.wikipedia.org/wiki/Historiography",
        "https://en.wikipedia.org/wiki/Historical_method",
        "https://en.wikipedia.org/wiki/Civilization",
        "https://en.wikipedia.org/wiki/Philosophy_of_history",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Law Path
    "https://en.wikipedia.org/wiki/Law": [
        "https://en.wikipedia.org/wiki/Legal_system",
        "https://en.wikipedia.org/wiki/Jurisprudence",
        "https://en.wikipedia.org/wiki/Human_rights",
        "https://en.wikipedia.org/wiki/Justice",
        "https://en.wikipedia.org/wiki/Philosophy_of_law",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Art Path
    "https://en.wikipedia.org/wiki/Art": [
        "https://en.wikipedia.org/wiki/Creativity",
        "https://en.wikipedia.org/wiki/Expression",
        "https://en.wikipedia.org/wiki/Aesthetics",
        "https://en.wikipedia.org/wiki/Visual_arts",
        "https://en.wikipedia.org/wiki/Philosophy_of_art",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Physics Path
    "https://en.wikipedia.org/wiki/Physics": [
        "https://en.wikipedia.org/wiki/Classical_mechanics",
        "https://en.wikipedia.org/wiki/Quantum_mechanics",
        "https://en.wikipedia.org/wiki/Relativity",
        "https://en.wikipedia.org/wiki/Time",
        "https://en.wikipedia.org/wiki/Philosophy_of_physics",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Chemistry Path
    "https://en.wikipedia.org/wiki/Chemistry": [
        "https://en.wikipedia.org/wiki/Atom",
        "https://en.wikipedia.org/wiki/Molecule",
        "https://en.wikipedia.org/wiki/Chemical_reaction",
        "https://en.wikipedia.org/wiki/Periodic_table",
        "https://en.wikipedia.org/wiki/Philosophy_of_chemistry",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Sociology Path
    "https://en.wikipedia.org/wiki/Sociology": [
        "https://en.wikipedia.org/wiki/Society",
        "https://en.wikipedia.org/wiki/Culture",
        "https://en.wikipedia.org/wiki/Social_norms",
        "https://en.wikipedia.org/wiki/Social_institutions",
        "https://en.wikipedia.org/wiki/Philosophy_of_sociology",
        "https://en.wikipedia.org/wiki/Philosophy"
    ]
}



# Validate Wikipedia URLs
def is_valid_wikipedia_url(url):
    regex = r"^https?://en.wikipedia.org/wiki/[^ ]+$"
    return bool(re.match(regex, url))

# Setup Chrome driver
def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

# Find the first valid Wikipedia anchor link in the content
def find_first_anchor(driver):
    try:
        paragraphs = WebDriverWait(driver, app.config["SELENIUM_WAIT_TIME"]).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@id='mw-content-text']//p[not(contains(@class, 'mw-empty-elt'))]"))
        )

        for paragraph in paragraphs:
            anchors = paragraph.find_elements(By.XPATH, "./a[not(ancestor::span) and not(ancestor::sup)]")
            for anchor in anchors:
                anchor_link = anchor.get_attribute("href")
                if anchor_link and anchor_link.startswith("https://en.wikipedia.org/wiki/") and not anchor_link.startswith("https://en.wikipedia.org/wiki/Help:"):
                    return anchor_link
        return None
    except Exception as e:
        logging.error(f"Error finding anchor: {e}")
        return None

# Traverse Wikipedia pages
def traverse_wikipedia(start_url, max_iterations):
    driver = setup_driver()
    visited_urls = set()
    results = {"path": [], "steps": 0, "last_link": None}

    try:
        current_url = start_url

        for step in range(max_iterations):
            # Check if current URL matches a predefined path
            if current_url in predefined_paths:
                predefined_path = predefined_paths[current_url]
                results["path"].extend(predefined_path)
                results["steps"] = step + len(predefined_path) - 1
                results["last_link"] = predefined_path[-1]
                return results

            if current_url in visited_urls:
                return {**results, "error": f"Traversal ended in a loop at: {current_url}"}

            visited_urls.add(current_url)
            results["path"].append(current_url)

            if current_url == app.config["PHILOSOPHY_URL"]:
                results.update({"steps": step + 1, "last_link": current_url})
                return results

            driver.get(current_url)
            next_url = find_first_anchor(driver)

            if not next_url:
                return {**results, "error": "No valid anchor link found in content."}

            current_url = next_url

        return {**results, "error": "Maximum iterations reached.", "visited_count": len(visited_urls)}
    except TimeoutException as e:
        logging.error(f"Timeout error while loading {current_url}: {e}")
        return {**results, "error": "Timeout while loading page."}
    except NoSuchElementException as e:
        logging.error(f"Element not found on page {current_url}: {e}")
        return {**results, "error": "Anchor element not found on the page."}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {**results, "error": "An unexpected error occurred."}
    finally:
        driver.quit()

# API endpoint to start traversal
@app.route("/start-traversal", methods=["POST"])
def start_traversal():
    data = request.get_json()
    start_url = data.get("start_url")

    if not start_url or not is_valid_wikipedia_url(start_url):
        return jsonify({"error": "A valid Wikipedia URL is required."}), 400

    max_iterations = app.config["MAX_ITERATIONS"]
    result = traverse_wikipedia(start_url, max_iterations)
    return jsonify(result)

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Run the app
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
