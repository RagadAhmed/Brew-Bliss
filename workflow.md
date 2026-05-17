# Brew Bliss Workflow

## Development Flow

1. Create or update product data in `data/sample_products.csv`.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run `python app.py` or `python run_local.py`.
4. The app creates `data/database.db` automatically if it is missing.
5. Browse the store, add products to the cart, and place a checkout order.
6. Log in as admin to manage products, categories, and orders.

## Application Architecture

- `app.py` contains the Flask app, routes, authentication, database setup, and admin logic.
- `templates/` contains all customer and admin HTML pages.
- `static/css/style.css` contains responsive business styling.
- `static/js/main.js` contains navbar, confirmation, and small interaction scripts.
- `data/sample_products.csv` contains seed product data.
- `data/database.db` stores users, admins, categories, products, cart activity, orders, and order items.

## Main User Paths

- Customer visits the home page.
- Customer reviews promotions, testimonials, categories, and featured products.
- Customer searches, sorts, paginates, or filters products.
- Customer opens a product details page.
- Customer reviews ingredients, rating, quantity, and related products.
- Customer adds items to the cart.
- Customer checks out with contact and delivery information.

## Admin Flow

- Admin logs in through `/admin/login`.
- Admin reviews dashboard analytics.
- Admin adds, edits, and deletes products.
- Admin manages categories.
- Admin reviews submitted orders.

## Database Workflow

- On startup, `init_db()` creates missing tables.
- Product seed data is imported from `sample_products.csv`.
- Existing seed products are updated by name so CSV changes can refresh local data.
- Orders are stored in `orders` and `order_items`.
- Customer cart behavior is kept in session and also recorded in the `cart` table for the requested schema.

## Admin Credentials

- Email: `admin@brewbliss.local`
- Password: `admin123`

Change these credentials before using the project beyond local learning.
