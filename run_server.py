#!/bin/python
#  Access using http://localhost:8888
#python -m SimpleHTTPServer 8888
#python -m CGIHTTPServer 8889
import http.server
from http.server import HTTPServer, CGIHTTPRequestHandler

class Handler(CGIHTTPRequestHandler):
    cgi_directories = ["/cgi-bin"]

PORT = 8189

httpd = HTTPServer(("", PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()
httpd.serve_forever()
