import os
import json
import re
import logging
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
# Assuming config defines Config.PHILOSOPHY_URL and Config.MAX_ITERATIONS
# Create a dummy Config class if you don't have one
class Config:
    PHILOSOPHY_URL = "https://en.wikipedia.org/wiki/Philosophy"
    MAX_ITERATIONS = 100 # Default value

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) # Setup basic logging

# Load predefined paths (optional, kept from original)
try:
    # Assuming predefined_paths.json is in the same directory as the script
    with open(os.path.join(os.path.dirname(__file__), "predefined_paths.json"), "r") as f:
        predefined_paths = json.load(f)
except Exception as e:
    logger.warning("Could not load predefined_paths.json: %s", e)
    predefined_paths = {}


def is_valid_wikipedia_url(url: str) -> bool:
    pattern = r"^https?://en\.wikipedia\.org/wiki/[^\s#]+$"
    # Basic check, ensure it's an English Wikipedia article link
    # Avoid fragment identifiers (#) in the main URL check
    return re.match(pattern, url.strip()) is not None and '#' not in url.split('/')[-1]


def find_first_link(url: str) -> str | None:
    """
    Finds the first valid, non-parenthesized link in the main body
    of a Wikipedia article.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        soup = BeautifulSoup(resp.text, "html.parser")

        # Find the main content area (usually within div#mw-content-text > div.mw-parser-output)
        content = soup.find("div", {"id": "mw-content-text"})
        if not content:
            logger.warning("Could not find div#mw-content-text in %s", url)
            return None
        parser_output = content.find("div", class_="mw-parser-output")
        if not parser_output:
            logger.warning("Could not find div.mw-parser-output in %s", url)
            # Fallback to using the whole content div if parser-output is missing
            parser_output = content

        # --- Attempt to remove elements that often contain irrelevant links ---
        # Selectors for common elements to ignore (infoboxes, hatnotes, navboxes, etc.)
        selectors_to_remove = [
            'table.infobox', 'div.infobox', 'div.hatnote', '.thumb', '.gallery',
            '.navbox', 'table.navbox', '.metadata', 'table.metadata', 'div.reflist',
            'ol.references', '#toc', '.sidebar', '.sistersitebox', '.portalbox',
             '.mw-empty-elt' # Remove potentially empty elements causing issues
        ]
        for selector in selectors_to_remove:
            for tag in parser_output.select(selector):
                tag.decompose() # Remove the tag and its content from the tree

        # --- Find the first valid link in paragraphs, outside parentheses ---
        # Iterate through main content elements, starting with paragraphs
        # Also check lists as sometimes the first link is there
        for element in parser_output.find_all(['p', 'ul', 'ol', 'li'], recursive=True):
            # Skip elements that are likely irrelevant (e.g., empty paragraphs after removal)
            if not element.get_text(strip=True):
                 continue

            parenthesis_level = 0
            # Iterate through the contents of the element (text and tags)
            for node in element.children: # Use .children for direct descendants
                if isinstance(node, NavigableString): # If it's plain text
                    for char in str(node):
                        if char == '(': parenthesis_level += 1
                        elif char == ')': parenthesis_level = max(0, parenthesis_level - 1) # Don't go below 0
                elif isinstance(node, Tag):
                    # Process text within the tag for parentheses first
                    inline_text = node.get_text()
                    # Check if the tag is a link (<a>) and we are outside parentheses
                    if node.name == 'a' and parenthesis_level == 0:
                        href = node.get('href')
                        # Check link validity
                        if href:
                             # Basic validity checks: starts with /wiki/, isn't a fragment
                            is_wiki_link = href.startswith('/wiki/')
                            is_fragment = '#' in href
                            is_red_link = 'redlink=1' in href # Skip non-existent pages

                            if is_wiki_link and not is_fragment and not is_red_link:
                                # More robust namespace and file checks
                                link_target = href.split('/')[-1]
                                if not re.match(r"^(File|Image|Category|Help|Portal|Special|Template|Wikipedia|Draft|TimedText|User|User_talk|MediaWiki|MediaWiki_talk|Template_talk|Help_talk|Category_talk|Portal_talk|Draft_talk|Education_program_talk|Module|Module_talk|Gadget|Gadget_talk|Gadget_definition|Gadget_definition_talk|Media|Topic):", link_target, re.IGNORECASE) and \
                                   "(disambiguation)" not in link_target:

                                    full_url = "https://en.wikipedia.org" + href
                                    # Final check to ensure it's a valid-looking article URL
                                    if is_valid_wikipedia_url(full_url) and full_url != url: # Avoid self-links
                                        logger.debug("Found valid link: %s in %s", full_url, url)
                                        return full_url

                    # Update parenthesis level based on text within the current tag (node)
                    # This ensures parentheses within nested tags are counted correctly before checking subsequent links.
                    for char in inline_text:
                        if char == '(': parenthesis_level += 1
                        elif char == ')': parenthesis_level = max(0, parenthesis_level - 1)


        logger.warning("No valid link found according to rules in %s", url)
        return None # No valid link found in any paragraph

    except requests.exceptions.RequestException as e:
        logger.error("Network error fetching %s: %s", url, e)
        return None
    except Exception as e:
        logger.exception("Error parsing or finding link in %s: %s", url, e) # Log full traceback
        return None


# Keep the traverse_wikipedia function largely the same
def traverse_wikipedia(start_url: str, max_iterations: int | None = None) -> dict:
    """
    Traverses Wikipedia by following the first valid link until Philosophy,
    a loop, max iterations, or an error occurs.
    """
    if not is_valid_wikipedia_url(start_url):
        return {"path": [], "steps": 0, "last_link": start_url,
                "error": "Invalid starting URL", "error_type": "invalid_start_url"}

    visited = set()
    path = []
    steps = 0
    limit = max_iterations if max_iterations is not None else Config.MAX_ITERATIONS

    # Check predefined paths (optional)
    if start_url in predefined_paths:
        seq = predefined_paths[start_url]
        return {"path": seq, "steps": len(seq) -1, "last_link": seq[-1] if seq else start_url} # Steps = transitions

    current = start_url
    try:
        for _ in range(limit):
            logger.info("Step %d: Visiting %s", steps, current)

            if current in visited:
                path.append(current) # Add the looping link to the path for clarity
                logger.warning("Loop detected at %s", current)
                return {"path": path, "steps": steps, "last_link": current,
                        "error": f"Loop detected at {current}", "error_type": "loop"}

            visited.add(current)
            path.append(current)

            if current == Config.PHILOSOPHY_URL:
                logger.info("Reached Philosophy!")
                return {"path": path, "steps": steps, "last_link": current}

            # Use the improved find_first_link function
            next_url = find_first_link(current)

            if not next_url:
                logger.error("No valid link found from %s", current)
                return {"path": path, "steps": steps, "last_link": current,
                        "error": "No valid link found according to rules", "error_type": "no_valid_link"}

            # Basic check to prevent immediate infinite loops if find_first_link returns the same URL (shouldn't happen with current logic)
            # if next_url == current:
            #      logger.error("find_first_link returned the same URL %s", current)
            #      return {"path": path, "steps": steps, "last_link": current,
            #              "error": "Link finding returned current URL", "error_type": "self_link_error"}

            current = next_url
            steps += 1 # Increment steps after a successful transition

        # If loop finishes without hitting conditions
        logger.warning("Maximum iterations (%d) reached", limit)
        return {"path": path, "steps": steps, "last_link": current,
                "error": f"Maximum iterations ({limit}) reached", "error_type": "max_iterations_reached"}

    except Exception as e:
        logger.exception("Traversal error during processing of %s: %s", current, e)
        # Include the current node in the path if an error occurs during its processing
        if current not in path:
             path.append(current)
        return {"path": path, "steps": steps, "last_link": path[-1] if path else start_url,
                 "error": f"An unexpected error occurred: {e}", "error_type": "runtime_error"}

