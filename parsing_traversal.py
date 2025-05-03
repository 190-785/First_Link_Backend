import re
import requests
from bs4 import BeautifulSoup
from config import Config


def traverse_parsing_only(start_url: str, max_iterations: int = Config.MAX_ITERATIONS) -> dict:
    visited = set()
    path = []
    current = start_url
    for step in range(max_iterations):
        if current in visited:
            return {"path": path, "error": f"Loop detected at {current}", "steps": step, "last_link": current, "error_type": "loop"}
        visited.add(current)
        path.append(current)
        if current == Config.PHILOSOPHY_URL:
            return {"path": path, "steps": step + 1, "last_link": current}
        resp = requests.get(current, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        for p in soup.select("#mw-content-text p:not(.mw-empty-elt)"):
            a = p.find("a", href=re.compile(r"^/wiki/"))
            if a and not a['href'].startswith("/wiki/Help:"):
                current = "https://en.wikipedia.org" + a['href']
                break
        else:
            return {"path": path, "error": "No valid anchor found", "steps": step + 1, "last_link": current, "error_type": "no_valid_link"}
    return {"path": path, "error": "Maximum iterations reached", "steps": max_iterations, "last_link": current, "error_type": "max_iterations_reached"}