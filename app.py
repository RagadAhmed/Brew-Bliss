import csv
import os
import sqlite3
from functools import wraps
from math import ceil
from werkzeug.security import check_password_hash, generate_password_hash
from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "database.db")
CSV_PATH = os.path.join(DATA_DIR, "sample_products.csv")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-this-secret")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT NOT NULL,
            description TEXT NOT NULL,
            ingredients TEXT DEFAULT '',
            rating REAL NOT NULL DEFAULT 4.8,
            promo_tag TEXT DEFAULT '',
            featured INTEGER NOT NULL DEFAULT 0,
            stock INTEGER NOT NULL DEFAULT 20,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_id TEXT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            address TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'New',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        """
    )
    existing_columns = {
        row["name"] for row in db.execute("PRAGMA table_info(products)").fetchall()
    }
    product_migrations = {
        "ingredients": "ALTER TABLE products ADD COLUMN ingredients TEXT DEFAULT ''",
        "rating": "ALTER TABLE products ADD COLUMN rating REAL NOT NULL DEFAULT 4.8",
        "promo_tag": "ALTER TABLE products ADD COLUMN promo_tag TEXT DEFAULT ''",
    }
    for column, statement in product_migrations.items():
        if column not in existing_columns:
            db.execute(statement)

    admin = db.execute("SELECT id FROM users WHERE email = ?", ("admin@brewbliss.local",)).fetchone()
    if admin is None:
        db.execute(
            "INSERT INTO users (name, email, password_hash, is_admin) VALUES (?, ?, ?, ?)",
            ("Brew Bliss Admin", "admin@brewbliss.local", generate_password_hash("admin123"), 1),
        )
    admin_account = db.execute(
        "SELECT id FROM admins WHERE email = ?", ("admin@brewbliss.local",)
    ).fetchone()
    if admin_account is None:
        db.execute(
            "INSERT INTO admins (name, email, password_hash) VALUES (?, ?, ?)",
            ("Brew Bliss Admin", "admin@brewbliss.local", generate_password_hash("admin123")),
        )

    count = db.execute("SELECT COUNT(*) AS total FROM products").fetchone()["total"]
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                db.execute(
                    "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                    (row["category"], f"Premium {row['category'].lower()} selections."),
                )
                existing = db.execute(
                    "SELECT id FROM products WHERE name = ?", (row["name"],)
                ).fetchone()
                fields = (
                    row["category"],
                    float(row["price"]),
                    row["image"],
                    row["description"],
                    row.get("ingredients", ""),
                    float(row.get("rating", 4.8)),
                    row.get("promo_tag", ""),
                    int(row["featured"]),
                    int(row["stock"]),
                    row["name"],
                )
                if existing:
                    db.execute(
                        """
                        UPDATE products
                        SET category = ?, price = ?, image = ?, description = ?,
                            ingredients = ?, rating = ?, promo_tag = ?, featured = ?, stock = ?
                        WHERE name = ?
                        """,
                        fields,
                    )
                else:
                    db.execute(
                        """
                        INSERT INTO products
                        (category, price, image, description, ingredients, rating, promo_tag,
                         featured, stock, name)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        fields,
                    )

    db.commit()
    db.close()


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def current_admin():
    admin_id = session.get("admin_id")
    if not admin_id:
        return None
    return get_db().execute("SELECT * FROM admins WHERE id = ?", (admin_id,)).fetchone()


@app.context_processor
def inject_globals():
    cart = session.get("cart", {})
    cart_count = sum(cart.values())
    return {
        "current_user": current_user(),
        "current_admin": current_admin(),
        "cart_count": cart_count,
    }


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_admin():
            flash("Admin access is required.", "danger")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped_view


def get_cart_items():
    cart = session.get("cart", {})
    items = []
    total = 0
    if not cart:
        return items, total

    product_ids = [int(pid) for pid in cart.keys()]
    placeholders = ",".join("?" for _ in product_ids)
    products = get_db().execute(
        f"SELECT * FROM products WHERE id IN ({placeholders})", product_ids
    ).fetchall()

    for product in products:
        quantity = cart.get(str(product["id"]), 0)
        subtotal = quantity * product["price"]
        total += subtotal
        items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
    return items, total


@app.route("/")
def home():
    db = get_db()
    featured = db.execute("SELECT * FROM products WHERE featured = 1 LIMIT 6").fetchall()
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    return render_template("index.html", featured=featured, categories=categories)


@app.route("/products")
def products():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    sort = request.args.get("sort", "featured")
    page = max(1, int(request.args.get("page", 1)))
    per_page = 8
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if category:
        query += " AND category = ?"
        params.append(category)

    count_query = query.replace("SELECT *", "SELECT COUNT(*) AS total")
    sort_options = {
        "price_low": "price ASC",
        "price_high": "price DESC",
        "rating": "rating DESC",
        "newest": "created_at DESC",
        "featured": "featured DESC, name ASC",
    }
    query += f" ORDER BY {sort_options.get(sort, sort_options['featured'])}"
    query += " LIMIT ? OFFSET ?"
    params_for_list = [*params, per_page, (page - 1) * per_page]

    db = get_db()
    total_products = db.execute(count_query, params).fetchone()["total"]
    total_pages = max(1, ceil(total_products / per_page))
    product_list = db.execute(query, params_for_list).fetchall()
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    return render_template(
        "products.html",
        products=product_list,
        categories=categories,
        search=search,
        selected_category=category,
        sort=sort,
        page=page,
        total_pages=total_pages,
    )


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        flash("Product not found.", "warning")
        return redirect(url_for("products"))
    related = db.execute(
        """
        SELECT * FROM products
        WHERE category = ? AND id != ?
        ORDER BY rating DESC
        LIMIT 4
        """,
        (product["category"], product["id"]),
    ).fetchall()
    return render_template("product_detail.html", product=product, related=related)


@app.route("/cart")
def cart():
    items, total = get_cart_items()
    return render_template("cart.html", items=items, total=total)


@app.post("/cart/add/<int:product_id>")
def add_to_cart(product_id):
    quantity = max(1, int(request.form.get("quantity", 1)))
    product = get_db().execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        flash("Product not found.", "warning")
        return redirect(url_for("products"))

    cart_data = session.get("cart", {})
    cart_data[str(product_id)] = cart_data.get(str(product_id), 0) + quantity
    session["cart"] = cart_data
    get_db().execute(
        "INSERT INTO cart (user_id, session_id, product_id, quantity) VALUES (?, ?, ?, ?)",
        (session.get("user_id"), session.get("_id", "guest"), product_id, quantity),
    )
    get_db().commit()
    flash("Added to cart.", "success")
    return redirect(request.referrer or url_for("cart"))


@app.post("/cart/update/<int:product_id>")
def update_cart(product_id):
    quantity = int(request.form.get("quantity", 1))
    cart_data = session.get("cart", {})
    if quantity <= 0:
        cart_data.pop(str(product_id), None)
    else:
        cart_data[str(product_id)] = quantity
    session["cart"] = cart_data
    flash("Cart updated.", "success")
    return redirect(url_for("cart"))


@app.post("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    cart_data = session.get("cart", {})
    cart_data.pop(str(product_id), None)
    session["cart"] = cart_data
    flash("Item removed.", "success")
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items, total = get_cart_items()
    if not items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("products"))

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        address = request.form["address"].strip()

        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO orders (user_id, customer_name, customer_email, address, total)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session.get("user_id"), name, email, address, total),
        )
        order_id = cursor.lastrowid
        for item in items:
            product = item["product"]
            db.execute(
                """
                INSERT INTO order_items
                (order_id, product_id, product_name, quantity, price)
                VALUES (?, ?, ?, ?, ?)
                """,
                (order_id, product["id"], product["name"], item["quantity"], product["price"]),
            )
        db.commit()
        session["cart"] = {}
        flash(f"Order #{order_id} placed successfully.", "success")
        return redirect(url_for("home"))

    return render_template("checkout.html", items=items, total=total)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        try:
            db = get_db()
            cursor = db.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
            db.commit()
            session["user_id"] = cursor.lastrowid
            flash("Welcome to Brew Bliss.", "success")
            return redirect(url_for("home"))
        except sqlite3.IntegrityError:
            flash("That email is already registered.", "danger")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash("Logged in successfully.", "success")
            return redirect(url_for("home"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("home"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        admin = get_db().execute("SELECT * FROM admins WHERE email = ?", (email,)).fetchone()
        if admin and check_password_hash(admin["password_hash"], password):
            session["admin_id"] = admin["id"]
            flash("Admin login successful.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin credentials.", "danger")
    return render_template("admin_login.html")


@app.route("/admin")
@admin_required
def admin_dashboard():
    db = get_db()
    products_count = db.execute("SELECT COUNT(*) AS total FROM products").fetchone()["total"]
    orders_count = db.execute("SELECT COUNT(*) AS total FROM orders").fetchone()["total"]
    revenue = db.execute("SELECT COALESCE(SUM(total), 0) AS total FROM orders").fetchone()["total"]
    customers_count = db.execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"]
    products_list = db.execute("SELECT * FROM products ORDER BY created_at DESC").fetchall()
    return render_template(
        "admin_dashboard.html",
        products=products_list,
        products_count=products_count,
        orders_count=orders_count,
        revenue=revenue,
        customers_count=customers_count,
    )


@app.route("/admin/products/new", methods=["GET", "POST"])
@admin_required
def admin_add_product():
    if request.method == "POST":
        save_product()
        flash("Product added.", "success")
        return redirect(url_for("admin_dashboard"))
    categories = get_db().execute("SELECT * FROM categories ORDER BY name").fetchall()
    return render_template("product_form.html", product=None, categories=categories)


@app.route("/admin/products/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_product(product_id):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        flash("Product not found.", "warning")
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        save_product(product_id)
        flash("Product updated.", "success")
        return redirect(url_for("admin_dashboard"))
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    return render_template("product_form.html", product=product, categories=categories)


@app.post("/admin/products/<int:product_id>/delete")
@admin_required
def admin_delete_product(product_id):
    get_db().execute("DELETE FROM products WHERE id = ?", (product_id,))
    get_db().commit()
    flash("Product deleted.", "success")
    return redirect(url_for("admin_dashboard"))


def save_product(product_id=None):
    category = request.form["category"].strip()
    get_db().execute(
        "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
        (category, f"Premium {category.lower()} selections."),
    )
    fields = (
        request.form["name"].strip(),
        category,
        float(request.form["price"]),
        request.form["image"].strip(),
        request.form["description"].strip(),
        request.form["ingredients"].strip(),
        float(request.form["rating"]),
        request.form["promo_tag"].strip(),
        1 if request.form.get("featured") else 0,
        int(request.form["stock"]),
    )
    db = get_db()
    if product_id:
        db.execute(
            """
            UPDATE products
            SET name = ?, category = ?, price = ?, image = ?, description = ?,
                ingredients = ?, rating = ?, promo_tag = ?, featured = ?, stock = ?
            WHERE id = ?
            """,
            (*fields, product_id),
        )
    else:
        db.execute(
            """
            INSERT INTO products
            (name, category, price, image, description, ingredients, rating,
             promo_tag, featured, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            fields,
        )
    db.commit()


@app.route("/admin/orders")
@admin_required
def admin_orders():
    orders = get_db().execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall()
    order_items = {}
    for order in orders:
        order_items[order["id"]] = get_db().execute(
            "SELECT * FROM order_items WHERE order_id = ?", (order["id"],)
        ).fetchall()
    return render_template("admin_orders.html", orders=orders, order_items=order_items)


@app.route("/admin/categories", methods=["GET", "POST"])
@admin_required
def admin_categories():
    db = get_db()
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form["description"].strip()
        if name:
            db.execute(
                "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                (name, description),
            )
            db.commit()
            flash("Category saved.", "success")
        return redirect(url_for("admin_categories"))
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    return render_template("admin_categories.html", categories=categories)


@app.post("/admin/categories/<int:category_id>/delete")
@admin_required
def admin_delete_category(category_id):
    db = get_db()
    category = db.execute("SELECT * FROM categories WHERE id = ?", (category_id,)).fetchone()
    if category:
        in_use = db.execute(
            "SELECT COUNT(*) AS total FROM products WHERE category = ?", (category["name"],)
        ).fetchone()["total"]
        if in_use:
            flash("Cannot delete a category that has products.", "warning")
        else:
            db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            db.commit()
            flash("Category deleted.", "success")
    return redirect(url_for("admin_categories"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5012, use_reloader=False)
