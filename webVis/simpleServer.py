import http.server
import socketserver
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8000

Handler = http.server.CGIHTTPRequestHandler

httpd = http.server.HTTPServer(("",PORT),Handler)

print("now serving:   ", os.getcwd(), "\nOn port ", PORT)

httpd.serve_forever()