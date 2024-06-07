from waitress import serve
import app
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    serve(app.app, host='0.0.0.0', port=5000, threads=6, 
          url_scheme='http', backlog=2048, max_request_header_size=4096, 
          max_request_body_size=1073741824, connection_limit=1000, 
          cleanup_interval=30, channel_timeout=120, asyncore_loop_timeout=1, 
          asyncore_use_poll=True, expose_tracebacks=False, log_socket_errors=True, 
    )
