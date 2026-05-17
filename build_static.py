import os
import shutil
from pathlib import Path

from app import app, get_db, init_db


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def clean_dist():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()


def copy_static_assets():
    shutil.copytree(ROOT / "static", DIST / "static")
    static_mode_js = DIST / "static" / "js" / "netlify-static.js"
    static_mode_js.write_text(
        """
document.querySelectorAll('form[action^="/cart/"], form[action="/checkout"]').forEach((form) => {
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        window.location.href = "/netlify-demo/";
    });
});
""".strip()
        + "\n",
        encoding="utf-8",
    )


def write_page(path, html):
    html = html.replace(
        '<script src="/static/js/main.js"></script>',
        '<script src="/static/js/main.js"></script>\n    <script src="/static/js/netlify-static.js"></script>',
    )
    if path == "/":
        output = DIST / "index.html"
    else:
        output = DIST / path.strip("/") / "index.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")


def export_route(client, route, output_path=None):
    response = client.get(route)
    if response.status_code not in (200, 302):
        raise RuntimeError(f"Could not export {route}: HTTP {response.status_code}")
    write_page(output_path or route, response.get_data(as_text=True))


def export_product_pages(client):
    with app.app_context():
        products = get_db().execute("SELECT id FROM products ORDER BY id").fetchall()
    for product in products:
        export_route(client, f"/product/{product['id']}")


def export_demo_notice():
    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Brew Bliss Demo Mode</title>
  <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
  <main class="auth-page">
    <section class="form-panel auth-panel">
      <p class="eyebrow">Netlify static demo</p>
      <h1>Storefront Preview</h1>
      <p>Brew Bliss is published on Netlify as a static storefront preview. Cart, checkout, login, and admin features require the Flask + SQLite backend and work locally with <code>python run_local.py</code>.</p>
      <a class="btn primary full" href="/">Back to Home</a>
    </section>
  </main>
</body>
</html>"""
    write_page("/netlify-demo/", html)


def main():
    os.environ.setdefault("SECRET_KEY", "netlify-static-build")
    init_db()
    clean_dist()
    copy_static_assets()
    with app.test_client() as client:
        export_route(client, "/")
        export_route(client, "/products")
        export_route(client, "/cart")
        export_product_pages(client)
    export_demo_notice()
    print(f"Static site exported to {DIST}")


if __name__ == "__main__":
    main()
