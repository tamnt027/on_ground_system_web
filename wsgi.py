from gevent.pywsgi import WSGIServer
from index import app


http_server = WSGIServer(("0.0.0.0", 8002), app)
http_server.serve_forever()