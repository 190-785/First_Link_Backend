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
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://first-link-delta.vercel.app"])
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')  # Default to production if not set
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')


# Function to run the Selenium script
def start_wiki_traversal(start_url, max_iterations=50):
    # Set up Chrome options for headless operation
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")  # Required for certain cloud environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Avoids shared memory issues in cloud
    chrome_options.add_argument("--disable-gpu")  # Optional: improves stability in some environments
    chrome_options.add_argument("--window-size=1920,1080")  # Set default window size

    # Initialize the Chrome driver with the specified options
    service = ChromeService()  # Configure Chrome service
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Initial traversal setup
    current_website = start_url
    results = {
        'path': [],  # Store the path taken
        'steps': 0,  # Track the number of steps taken
        'last_link': None  # Track the last visited link
    }
    visited_urls = set()  # Track visited URLs to prevent self-loops
    loop_counter = 0

    # Loop until we reach the Philosophy page, detect a self-loop, or hit the iteration limit
    while current_website != "https://en.wikipedia.org/wiki/Philosophy":
        if current_website in visited_urls:
            results['path'].append(current_website)
            results['error'] = f"Traversal ended in a loop at: {current_website}"
            break  # Stop if we've already visited this URL

        visited_urls.add(current_website)  # Add the current website to the visited set
        results['path'].append(current_website)  # Record the current website in the path
        
        if loop_counter >= max_iterations:
            results['error'] = "Maximum iterations reached, traversal stopped."
            break  # Exit the loop after reaching the max iterations

        loop_counter += 1  # Increment the loop counter
        results['steps'] += 1  # Increment step count

        try:
            # Open the website
            print(f"Visiting: {current_website}")
            driver.get(current_website)

            # Wait for the page to load and find all paragraphs in the specific <div> tag
            paragraphs = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@id='mw-content-text' and contains(@class, 'mw-body-content')]//p[not(contains(@class, 'mw-empty-elt'))]"))
            )

            first_anchor_found = False  # Track if a direct anchor is found

            # Loop through all paragraphs to find the first valid direct child anchor tag
            for paragraph in paragraphs:
                anchors = paragraph.find_elements(By.XPATH, "./a[not(ancestor::span) and not(ancestor::sup)] | ./b/a[not(ancestor::span) and not(ancestor::sup)] | ./i/a[not(ancestor::span) and not(ancestor::sup)]")

                for anchor in anchors:
                    anchor_link = anchor.get_attribute("href")

                    # Skip links that start with "https://en.wikipedia.org/wiki/Help:"
                    if anchor_link.startswith("https://en.wikipedia.org/wiki/Help:"):
                        continue  # Skip this anchor and move to the next

                    # If a valid link is found, update the current website to the clicked link
                    current_website = anchor_link
                    results['last_link'] = current_website  # Update the last visited link
                    first_anchor_found = True  # Set flag to true when an anchor is found
                    break  # Stop after finding the first valid anchor tag
                
                # Break out of the paragraph loop if an anchor was found
                if first_anchor_found:
                    break

            # If no valid anchor is found in any paragraph, break the loop
            if not first_anchor_found:
                results['error'] = 'No direct anchor tag found in any paragraph'
                break

        except Exception as e:
            # Handle exceptions and store the error message
            results['error'] = f"An error occurred: {str(e)}"
            break  # Break the loop if an error occurs

    driver.quit()  # Close the browser
    return results  # Return the results

@app.route('/start-traversal', methods=['POST'])
def traverse_wikipedia():
    data = request.get_json()
    start_url = data.get("start_url")  # Get the starting URL
    result = start_wiki_traversal(start_url)  # Run traversal function
    return jsonify(result)  # Return results as JSON


@app.route('/api', methods=['GET'])
def api():
    return {"message": "Hello from Flask Backend!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)