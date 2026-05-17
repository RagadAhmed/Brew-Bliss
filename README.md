# Brew Bliss

Brew Bliss is a production-style, beginner-friendly coffee shop e-commerce website built with HTML, CSS, JavaScript, Python Flask, and SQLite. It is designed as a realistic premium coffee business website with storefront pages, checkout, customer accounts, and an admin panel.

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

If port `5000` is already showing another project, use the dedicated Brew Bliss runner instead.

```bash
python run_local.py
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

## Database

The SQLite database is stored at:

```text
data/database.db
```

The app creates and seeds the database automatically from:

```text
data/sample_products.csv
```

Tables included:

- `users`
- `admins`
- `categories`
- `products`
- `cart`
- `orders`
- `order_items`

To reset the store data, stop Flask, delete `data/database.db`, and run `python app.py` again.

## Screenshots

Add screenshots here after running the app locally:

- Home page: `static/images/screenshots/home.png`
- Product page: `static/images/screenshots/products.png`
- Product details: `static/images/screenshots/product-detail.png`
- Cart and checkout: `static/images/screenshots/checkout.png`
- Admin dashboard: `static/images/screenshots/admin.png`

## Troubleshooting

If the browser says `127.0.0.1 refused to connect`, the server is not running. Start it again:

```bash
python run_local.py
```

If another website opens on port `5000`, use:

```text
http://127.0.0.1:5012
```

If products do not show, delete `data/database.db` and run the app again so it can import `data/sample_products.csv`.

If `flask` is not found, activate your virtual environment and run:

```bash
pip install -r requirements.txt
```

## Image Prompts

The project uses Unsplash placeholder links in `data/sample_products.csv` and local SVG fallbacks in `static/images/`. Replace product image URLs or local files with final brand photography when available.

Homepage banner prompt:

```text
Boutique artisanal coffee shop interior, ultra-modern Scandinavian design, warm walnut wood textures mixed with elegant white Calacatta marble counters, soft natural light streaming through large matte-black grid windows, minimal premium espresso machine with subtle realistic steam rising, shallow depth of field, high-end editorial commercial interior photography, photorealistic, cinematic composition, shot on 35mm lens, f/2.8, warm cozy ambient color grading, website hero asset ready --ar 16:9
```

Product photography prompt:

```text
High-end commercial product photography of [a single hot latte with intricate tulip latte art in a matte ceramic charcoal cup / a flaky golden croissant on a small minimalist plate / a clear glass of iced cold brew coffee with condensation droplets], placed on a clean textured concrete countertop, soft directional side-lighting, blurred background showing a hint of a modern coffee shop, sharp focus on the item texture, appetizing, elegant, studio lighting, professional e-commerce store catalog ready --ar 4:3
```
