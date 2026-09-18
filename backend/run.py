import os
import socket
from app import create_app
from app.extensions import db

app = create_app(os.environ.get("FLASK_ENV", "development"))

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
    port = int(os.environ.get("PORT", 0))
    if port == 0:
        port = 5001 if is_port_in_use(5000) else 5000

    print(f"[STARTING] FoodRescue Backend running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
