# Brew Bliss

Brew Bliss is a premium coffee shop e-commerce website for showcasing coffee drinks, bakery items, roasted beans, promotions, and a modern online ordering experience.

Live website:

```text
https://brew-blisscoffee.netlify.app/
```

## Website Overview

Brew Bliss is designed to look and feel like a real coffee business storefront. The public website includes a polished homepage, product catalog, product detail pages, promotional content, customer trust sections, and a responsive layout for desktop, tablet, and mobile visitors.

The full project also includes a Flask and SQLite backend for cart, checkout, customer accounts, order storage, and admin management.

## Main Functionality

- Premium homepage with coffee shop branding
- Eye-catching hero banner
- Featured product section
- Product categories
- Customer testimonials
- Promotional banner
- Newsletter section
- Responsive navigation
- Mobile-friendly design
- Product catalog with search
- Category filtering
- Product sorting
- Product pagination
- Product ratings
- Product detail pages
- Product ingredients
- Related products
- Shopping cart flow
- Checkout form
- Customer register, login, and logout
- Flash messages and loading states
- Admin login
- Admin dashboard analytics
- Product add, edit, and delete tools
- Category management
- Customer order viewing

## Public Website Pages

- Home
- Products
- Product Details
- Cart Preview
- Netlify Demo Notice

## Backend Features

The complete Flask version supports:

- Secure password hashing
- Session management
- SQLite database storage
- Customer accounts
- Admin accounts
- Cart tracking
- Checkout order creation
- Order item storage
- Product and category management

## Database Coverage

The project includes SQLite tables for:

- `users`
- `admins`
- `categories`
- `products`
- `cart`
- `orders`
- `order_items`

Sample coffee products are included in `data/sample_products.csv`.

## Netlify Version

The Netlify website is published as a static storefront preview. Public browsing pages are available online, including the homepage, catalog, and product detail pages.

Because Netlify static hosting does not run a persistent Flask server or SQLite database, backend actions such as checkout, login, registration, and admin management are shown as demo-mode actions on the live Netlify site.

For a fully live production e-commerce system, the Flask backend should be hosted on a Python backend platform and connected to a production database.

## Design Style

- Coffee-inspired color palette
- Premium cafe look and feel
- Soft shadow cards
- Rounded product frames
- Consistent product image sizing
- Smooth hover effects
- Clean typography
- Professional business layout
- Responsive grid system
- Modern admin dashboard styling

## Admin Credentials

```text
Email: admin@brewbliss.local
Password: admin123
```

These credentials are for the Flask backend version of the project.

## Future Improvements

- Connect a hosted Flask backend
- Add real payment processing
- Add customer order history
- Add product reviews
- Add inventory updates after checkout
- Add coupon codes
- Add email order confirmations
- Add AI coffee recommendations
- Add AI-generated product descriptions for admins
