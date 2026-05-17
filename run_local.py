from wsgiref.simple_server import make_server

from app import app, init_db


if __name__ == "__main__":
    init_db()
    host = "127.0.0.1"
    port = 5012
    print(f"Brew Bliss is running at http://{host}:{port}")
    with make_server(host, port, app) as server:
        server.serve_forever()
