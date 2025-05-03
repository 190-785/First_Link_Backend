# Wikipedia First Link Rule Traversal API

This project implements an API that traverses Wikipedia articles based on the **First Link Rule**, where each article links to the next article in the series until it reaches the **Philosophy** page. It supports both **Selenium‑based** traversal and **Parsing‑based** traversal (using BeautifulSoup).

---

## Features

- **Selenium Traversal**: Uses the browser automation tool Selenium to simulate user browsing on Wikipedia.
- **Parsing Traversal**: Uses `requests` and `BeautifulSoup` for parsing the HTML to find the first link—no browser required.
- **API**: Exposes a simple POST endpoint for starting the traversal with a given Wikipedia URL.
- **Error Handling**: Detects loops, dead ends, and iteration limits with clear error messages.

---

## Requirements

### Python 3.12+

### Docker (optional, for containerized deployments)

#### Python Dependencies

Install via `requirements.txt`:

```bash
Flask==2.3.2
Flask-Cors==3.0.10
gunicorn==20.1.0
selenium==4.11.2
webdriver-manager==4.0.2
beautifulsoup4==4.12.2
requests==2.31.0
Werkzeug==2.3.6
```

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/wikipedia-first-link-rule.git
cd wikipedia-first-link-rule
```

### 2. Install Dependencies

#### Local (pip)

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: `venv\Scripts\activate`
pip install -r requirements.txt
```

#### Containerized (Docker)

```bash
docker build -t wikipedia-traversal .
docker run -p 10000:10000 wikipedia-traversal
```

---

## Configuration

Environment variables are loaded via a `.env` file or your environment. Key values:

```env
FLASK_ENV=development
SECRET_KEY=your_secret_key
MAX_ITERATIONS=30
PHILOSOPHY_URL=https://en.wikipedia.org/wiki/Philosophy
ALLOWED_ORIGINS=https://yourfrontenddomain.com
```

---

## API Endpoints

### POST `/start-traversal`

Start a traversal from a Wikipedia URL.

**Request Body** (JSON):

```json
{
    "start_url": "https://en.wikipedia.org/wiki/Physics"
}
```

**Response**:

```json
{
    "path": [
        "https://en.wikipedia.org/wiki/Physics",
        "...",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],
    "steps": 7,
    "last_link": "https://en.wikipedia.org/wiki/Philosophy",
    "error": "Loop detected at ..."   // optional
}
```

### GET `/`

Health check:

```json
{
    "status": "Backend is running"
}
```

---

## Traversal Logic

### Selenium-based (`traversal.py`)

- Launch headless Chrome via Selenium.
- Navigate to the page, locate the first valid `<a>` in the main content, follow it.
- Stops on Philosophy, loop detection, or max iterations.

### Parsing-based (`traversal.py` or `parsing_traversal.py`)

- Use `requests.get()` to fetch HTML.
- Use BeautifulSoup to parse `<div id="mw-content-text">` paragraphs.
- Remove parentheses to avoid invalid links.
- Follow the first `<a href="/wiki/...">` that isn’t a Help page.

---

## Predefined Paths

`predefined_paths.json` contains precomputed link sequences for common articles. If the start URL matches a key, the API returns the stored path immediately (fast response).

---

## Benchmark Results

Running `parsing_traversal.py` shows:

| Method       | Avg Time (single traversal) |
| ------------ | --------------------------- |
| Selenium     | ~2.5 s                      |
| Parsing-only | ~0.08 s                     |

**Conclusion:** Parsing-only is ~30× faster and uses far less memory. Use Selenium only when necessary.

---

## Docker Deployment

1. **Build** the image:

     ```bash
     docker build -t wikipedia-traversal .
     ```

2. **Run** the container:

     ```bash
     docker run -p 10000:10000 wikipedia-traversal
     ```

---

## Troubleshooting

- **404 on `/start-traversal`**: Ensure you’re POSTing to the correct route and that your deployment is serving the Flask app (not a frontend).
- **Loop detected**: The link path has circled back to a previous article.
- **No valid anchor found**: The page format may have changed or no valid first link exists.
- **Max iterations reached**: Increase `MAX_ITERATIONS` in your config if needed.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
