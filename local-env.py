from app import db
import app
import os
import ssl

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.join(CURRENT_DIR, 'certs/cert.pem')
KEY = os.path.join(CURRENT_DIR, 'certs/key.pem')

context = ssl.SSLContext()
context.load_cert_chain(CERT, KEY)


if __name__ == '__main__':
    with app.app.app_context():
        db.create_all()
    app.app.run(debug=True, host='0.0.0.0', port=5003, ssl_context=context)