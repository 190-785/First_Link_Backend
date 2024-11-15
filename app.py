from flask import Flask, jsonify, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
import chromedriver_autoinstaller

# Automatically install the appropriate ChromeDriver
chromedriver_autoinstaller.install()

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(
    app,
    origins=["https://first-link-delta.vercel.app"],
    methods=["GET", "POST", "PUT", "DELETE"],
    supports_credentials=True,
)

# Set app configurations
app.config["ENV"] = os.getenv("FLASK_ENV", "production")  # Default to production
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")

# Function to run the Selenium script
def start_wiki_traversal(start_url, max_iterations=50):
    """
    Traverses Wikipedia starting from the given URL until it reaches the Philosophy page,
    encounters a self-loop, or reaches the maximum number of iterations.
    """
    # Set up Chrome options for headless operation
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")  # Required for certain environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Avoid shared memory issues
    chrome_options.add_argument("--disable-gpu")  # Improve stability
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size

    # Initialize the Chrome driver with the specified options
    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Initialize traversal setup
    current_website = start_url
    results = {
        "path": [],  # Store the path taken
        "steps": 0,  # Count the number of steps
        "last_link": None,  # Track the last visited link
    }
    visited_urls = set()  # Track visited URLs to detect self-loops
    loop_counter = 0

    # Loop to traverse Wikipedia pages
    while current_website != "https://en.wikipedia.org/wiki/Philosophy":
        # Check for self-loop
        if current_website in visited_urls:
            results["path"].append(current_website)
            results["error"] = f"Traversal ended in a loop at: {current_website}"
            break

        # Add the current URL to the visited set
        visited_urls.add(current_website)
        results["path"].append(current_website)

        # Check for maximum iterations
        if loop_counter >= max_iterations:
            results["error"] = "Maximum iterations reached, traversal stopped."
            break

        # Increment counters
        loop_counter += 1
        results["steps"] += 1

        try:
            # Open the current website
            print(f"Visiting: {current_website}")
            driver.get(current_website)

            # Wait for page content to load and find all paragraphs
            paragraphs = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        "//div[@id='mw-content-text' and contains(@class, 'mw-body-content')]//p[not(contains(@class, 'mw-empty-elt'))]",
                    )
                )
            )

            # Loop through paragraphs to find the first valid direct child anchor tag
            first_anchor_found = False
            for paragraph in paragraphs:
                anchors = paragraph.find_elements(
                    By.XPATH,
                    "./a[not(ancestor::span) and not(ancestor::sup)] | ./b/a[not(ancestor::span) and not(ancestor::sup)] | ./i/a[not(ancestor::span) and not(ancestor::sup)]",
                )

                for anchor in anchors:
                    anchor_link = anchor.get_attribute("href")

                    # Skip unwanted links
                    if anchor_link.startswith("https://en.wikipedia.org/wiki/Help:"):
                        continue

                    # Update the current website to the found link
                    current_website = anchor_link
                    results["last_link"] = current_website
                    first_anchor_found = True
                    break

                if first_anchor_found:
                    break

            # Handle case where no valid anchor is found
            if not first_anchor_found:
                results["error"] = "No valid direct anchor tag found in any paragraph."
                break

        except Exception as e:
            # Handle exceptions and log the error
            results["error"] = f"An error occurred: {str(e)}"
            break

    # Quit the browser
    driver.quit()

    return results

# Route to start Wikipedia traversal
@app.route("/start-traversal", methods=["POST"])
def traverse_wikipedia():
    """
    Handles POST requests to initiate Wikipedia traversal.
    Expects JSON payload with `start_url`.
    """
    try:
        data = request.get_json()
        start_url = data.get("start_url")

        if not start_url:
            return jsonify({"error": "start_url is required"}), 400

        # Call traversal function
        result = start_wiki_traversal(start_url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Simple API health check endpoint
@app.route("/api", methods=["GET"])
def api():
    """
    Health check endpoint for the Flask backend.
    """
    return {"message": "Hello from Flask Backend!"}

# Main entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
