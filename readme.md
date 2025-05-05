

# First Link Project

An interactive full‑stack application that demonstrates Wikipedia traversal based on the “First Link Rule” — the observation that repeatedly clicking the first link in the main text of a Wikipedia article often leads to the *Philosophy* page.

[Live Demo](https://first-link-delta.vercel.app)

---

## Table of Contents

1. [About the Project](#about-the-project)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Repositories](#repositories)
5. [Setup & Installation](#setup--installation)

   * [Backend](#backend)
   * [Frontend](#frontend)
6. [Environment & Configuration](#environment--configuration)
7. [API Endpoints](#api-endpoints)
8. [How It Works](#how-it-works)
9. [Custom Tailwind Configuration](#custom-tailwind-configuration)
10. [Project Structure](#project-structure)
11. [License](#license)
12. [Acknowledgments](#acknowledgments)

---

## About the Project

**First Link Project** algorithmically follows the first in‑article hyperlink on Wikipedia pages, visualizing the path until it either reaches the *Philosophy* page, encounters a loop, or hits a dead end. It cleanly separates concerns between a Python‑powered API backend and a lightning‑fast React frontend.

---

## Features

* **Live Traversal**
  Enter any Wikipedia URL and watch the path unfold in real time.
* **Dual Traversal Modes**

  * **Parsing‑based** (BeautifulSoup) for lightweight servers
  * **Selenium‑based** for full browser simulation
* **Loop & Dead‑End Detection**
  Automatically stops on cycles or articles without valid first links.
* **Modular Architecture**
  Independently deployable frontend/backend, containerized via Docker.
* **Interactive UI**
  Branded Tailwind CSS theme with reusable React components.

---

## Tech Stack

* **Frontend**: React.js + Vite + Tailwind CSS
* **Backend**: Python 3.12+, Flask, BeautifulSoup, Requests (Selenium optional)
* **Containerization**: Docker
* **Deployment**: Vercel (frontend), Render (backend)

---

## Repositories

* **Frontend**: [https://github.com/190-785/First\_Link](https://github.com/190-785/First_Link)
* **Backend**: [https://github.com/190-785/First\_Link\_Backend](https://github.com/190-785/First_Link_Backend)

---

## Setup & Installation

### Backend

1. Clone the backend repo

   ```bash
   git clone https://github.com/190-785/First_Link_Backend.git
   cd First_Link_Backend
   ```
2. Create a virtual environment & install dependencies

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. (Optional) Run with Docker

   ```bash
   docker build -t wikipedia-traversal .
   docker run -p 10000:10000 wikipedia-traversal
   ```
4. Start the Flask server

   ```bash
   flask run --port 10000
   ```

### Frontend

1. Clone the frontend repo

   ```bash
   git clone https://github.com/190-785/First_Link.git
   cd First_Link
   ```
2. Install & start dev server

   ```bash
   npm install
   npm run dev
   ```
3. Open in browser
   Navigate to [http://localhost:5173](http://localhost:5173).

---

## Environment & Configuration

Set these env variables in a `.env` file at the root of your backend directory:

```env
FLASK_ENV=development
SECRET_KEY=your_secret_key
MAX_ITERATIONS=30
PHILOSOPHY_URL=https://en.wikipedia.org/wiki/Philosophy
ALLOWED_ORIGINS=http://localhost:5173
```

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

## How It Works

1. **User Input**
   Frontend sends the starting Wikipedia URL to the backend.
2. **Traversal Engine**

   * **Parsing mode**: `requests` + BeautifulSoup to extract the first valid link.
   * **Selenium mode**: headless Chrome for link extraction.
3. **Loop/Dead‑End Detection**
   Tracks visited URLs to prevent infinite cycles.
4. **Termination**
   Stops when reaching the *Philosophy* page or hitting a loop/dead‑end.
5. **Visualization**
   Frontend renders the full link path in a user‑friendly interface.

---

## Custom Tailwind Configuration

Extended in `tailwind.config.js` for a purple‑themed palette:

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        darkPurple: '#433878',
        mediumPurple: '#7e60bf',
        lightPurple: '#e4b1f0',
        palePurple: '#ffe1ff',
      },
    },
  },
};
```

Use in your markup:

```html
<div class="bg-darkPurple text-palePurple p-4">
  First Link Rule
</div>
```

---

## Project Structure

```plaintext
.
├── First_Link/               # React + Vite frontend
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── tailwind.config.js
└── First_Link_Backend/       # Flask backend
    ├── app.py
    ├── parsing_traversal.py
    ├── traversal.py
    ├── predefined_paths.json
    ├── requirements.txt
    └── Dockerfile
```

---

## License

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This project (both frontend & backend) is licensed under the **GNU General Public License v3.0**.
See the [LICENSE](https://github.com/190-785/First_Link_Backend/blob/main/LICENSE) file for full terms.

---

## Acknowledgments

* **Not David** – for the inspiring “First Link Rule” video:
  [https://youtu.be/-llumS2rA8I?feature=shared](https://youtu.be/-llumS2rA8I?feature=shared)
* **Wikipedia** – for the open REST API that powers this project
* **Open‑source community** – for all the incredible tools and libraries used
