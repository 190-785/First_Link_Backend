
# First Link Backend

A Python Flask API that powers the “First Link Rule” project by fetching and following the first link of any Wikipedia article until it reaches the *Philosophy* page, detects a loop, or hits a dead end. Supports both parsing-based traversal (BeautifulSoup) and optional Selenium-based traversal.

[Live Demo (Frontend)](https://first-link-delta.vercel.app)

---

## Table of Contents

1. [About](#about)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Setup & Installation](#setup--installation)
5. [Configuration](#configuration)
6. [API Endpoints](#api-endpoints)
7. [Project Structure](#project-structure)
8. [License](#license)
9. [Acknowledgments](#acknowledgments)

---

## About

This service handles traversal logic for the First Link Project. It exposes endpoints to start a traversal from any Wikipedia URL, returning the full path, step count, and any errors encountered.

---

## Features

* **Parsing-Based Traversal** with `requests` + BeautifulSoup for lightweight environments
* **Selenium-Based Traversal** (optional) for full browser simulation
* **Loop & Dead-End Detection** to prevent infinite cycles
* **Configurable Limits** (max iterations, target URL)
* **Docker Support** for containerized deployment

---

## Tech Stack

* **Language**: Python 3.12+
* **Framework**: Flask
* **HTTP**: Requests
* **HTML Parsing**: BeautifulSoup4
* **Browser Automation**: Selenium (optional)
* **Containerization**: Docker

---

## Setup & Installation

### Local Development

```bash
git clone https://github.com/190-785/First_Link_Backend.git
cd First_Link_Backend
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run --port 10000
```

### Docker

```bash
docker build -t first-link-backend .
docker run -p 10000:10000 first-link-backend
```

---

## Configuration

Create a `.env` file in the project root with:

```env
FLASK_ENV=development
SECRET_KEY=your_secret_key
MAX_ITERATIONS=30
PHILOSOPHY_URL=https://en.wikipedia.org/wiki/Philosophy
ALLOWED_ORIGINS=http://localhost:5173
USE_SELENIUM=false
```

* `USE_SELENIUM`: set to `true` to enable Selenium mode.

---

## API Endpoints

### POST `/start-traversal`

**Request Body** (JSON):

```json
{
  "start_url": "https://en.wikipedia.org/wiki/Physics"
}
```

**Response** (JSON):

```json
{
  "path": [
    "https://en.wikipedia.org/wiki/Physics",
    "...",
    "https://en.wikipedia.org/wiki/Philosophy"
  ],
  "steps": 7,
  "last_link": "https://en.wikipedia.org/wiki/Philosophy",
  "error": null
}
```

### GET `/`

**Response** (JSON):

```json
{
  "status": "Backend is running"
}
```

---

## Project Structure

```plaintext
First_Link_Backend/
├── app.py                   # Flask application
├── parsing_traversal.py     # BeautifulSoup-based traversal logic
├── traversal.py             # Core traversal engine
├── predefined_paths.json    # Example path sets (optional)
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container build instructions
└── .env.example             # Sample environment variables
```

---

## License

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This backend is licensed under the **GNU General Public License v3.0**.
See the [LICENSE](LICENSE) file for full terms.

---

## Acknowledgments

* **Not David** – For the inspiring “First Link Rule” video: [https://youtu.be/-llumS2rA8I?feature=shared](https://youtu.be/-llumS2rA8I?feature=shared)
* **Wikipedia** – For the open REST API
* **Open‑source community** – For all the libraries and tools used in this project
