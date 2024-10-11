from waitress import serve
import app
import logging
from app import db
import database
import os
import ssl
import os

if __name__ == '__main__':
      
      # DB ENVIRONMENT VARIABLES
      DB_HOST = os.getenv('DB_HOST')
      DB_PORT = os.getenv('DB_PORT')
      DB_USER = os.getenv('DB_USER')
      DB_PASSWORD = os.getenv('DB_PASSWORD')
      DB_NAME = os.getenv('DB_NAME')

      CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
      CERT = os.path.join(CURRENT_DIR, 'certs/cert.pem')
      KEY = os.path.join(CURRENT_DIR, 'certs/key.pem')

      context = ssl.SSLContext()
      context.load_cert_chain(CERT, KEY)


      db_pass = DB_PASSWORD.replace('@', '%40')
      
      database = database.Database()
      database.create_DB()
      
      with app.app.app_context():
            db.create_all()
      logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

      serve(app.app, host='0.0.0.0', port=5000, threads=6, 
            url_scheme='https', backlog=2048, max_request_header_size=4096, 
            max_request_body_size=1073741824, connection_limit=1000, 
            cleanup_interval=30, channel_timeout=120, asyncore_loop_timeout=1, 
            asyncore_use_poll=True, expose_tracebacks=False, log_socket_errors=True, ssl_context=context 
      )
