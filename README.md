# Brew Bliss

Brew Bliss is a production-style, beginner-friendly coffee shop e-commerce website built with HTML, CSS, JavaScript, Python Flask, and SQLite. It is designed as a realistic premium coffee business website with storefront pages, checkout, customer accounts, and an admin panel.

Live Netlify storefront:

```text
https://brew-blisscoffee.netlify.app/
```

## Features

- Home page with rich coffee shop styling
- Product catalog
- Product details
- Search and category filtering
- Sorting and pagination
- Product ratings, ingredients, and related products
- Shopping cart
- Checkout and order storage
- Customer registration and login
- Admin login
- Admin dashboard
- Add, edit, and delete products
- Manage categories
- View customer orders
- Responsive modern UI
- Testimonials, promotions, and newsletter section
- Flash messages and loading states

## Project Structure

```text
Brew_Bliss/
  app.py
  run_local.py
  build_static.py
  netlify.toml
  requirements.txt
  data/
    database.db
    sample_products.csv
  static/
    css/style.css
    js/main.js
    images/
  templates/
  workflow.md
  questions.md
  README.md
```

## Setup

1. Open the project folder in VS Code or CMD.

```bash
cd C:\Users\3214f\Codex_Projects\Brew_Bliss
```

2. Create a virtual environment.

```bash
python -m venv .venv
```

3. Activate it on Windows CMD.

```bash
.venv\Scripts\activate
```

4. Install the required libraries.

```bash
pip install -r requirements.txt
```

5. Run the app.

```bash
python app.py
```

6. Open this URL in your browser.

```text
http://127.0.0.1:5012
```

## Required Libraries

- Flask
- Werkzeug

## Publish on Netlify

Netlify is a static hosting platform. This project includes a Netlify-ready static storefront export for the public pages. The full cart, checkout, login, SQLite, and admin backend still require Flask and run locally with `python run_local.py`.

1. Push this repository to GitHub.
2. Open Netlify and choose `Add new site` then `Import an existing project`.
3. Select the GitHub repository.
4. Netlify will read `netlify.toml` automatically.
5. Confirm these settings:

```text
Build command: pip install -r requirements.txt && python build_static.py
Publish directory: dist
```

6. Click `Deploy site`.

The Netlify build exports:

- Home page
- Product catalog
- Product detail pages
- Static cart preview
- A demo notice page for checkout, login, and admin links

For a live production e-commerce backend, deploy Flask separately on a Python host such as Render, Railway, Fly.io, or a VPS, then connect it to a production database.

## Admin Login

```text
Email: admin@brewbliss.local
Password: admin123
```

Change this password before using the project for anything beyond local practice.

