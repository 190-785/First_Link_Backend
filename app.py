from flask import Flask, jsonify, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://first-link-delta.vercel.app"])
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')  # Default to production
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')


# Function to run the Selenium script
def start_wiki_traversal(start_url, max_iterations=50):
    # Set up Chrome options for headless operation
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # Initialize the Chrome driver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    # Traversal logic
    current_website = start_url
    results = {'path': [], 'steps': 0, 'last_link': None}
    visited_urls = set()
    loop_counter = 0

    while current_website != "https://en.wikipedia.org/wiki/Philosophy":
        if current_website in visited_urls:
            results['path'].append(current_website)
            results['error'] = f"Traversal ended in a loop at: {current_website}"
            break

        visited_urls.add(current_website)
        results['path'].append(current_website)
        if loop_counter >= max_iterations:
            results['error'] = "Maximum iterations reached."
            break

        loop_counter += 1
        results['steps'] += 1

        try:
            driver.get(current_website)
            paragraphs = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@id='mw-content-text']//p[not(contains(@class, 'mw-empty-elt'))]"))
            )

            first_anchor_found = False
            for paragraph in paragraphs:
                anchors = paragraph.find_elements(By.XPATH, "./a")
                for anchor in anchors:
                    anchor_link = anchor.get_attribute("href")
                    if anchor_link.startswith("https://en.wikipedia.org/wiki/Help:"):
                        continue
                    current_website = anchor_link
                    results['last_link'] = current_website
                    first_anchor_found = True
                    break
                if first_anchor_found:
                    break

            if not first_anchor_found:
                results['error'] = 'No valid anchor found.'
                break

        except Exception as e:
            results['error'] = f"An error occurred: {str(e)}"
            break

    driver.quit()
    return results


@app.route('/start-traversal', methods=['POST'])
def traverse_wikipedia():
    data = request.get_json()
    start_url = data.get("start_url")
    if not start_url:
        return jsonify({"error": "Missing 'start_url'"}), 400

    result = start_wiki_traversal(start_url)
    return jsonify(result)


@app.route('/api', methods=['GET'])
def api():
    return {"message": "Hello from Flask Backend!"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
