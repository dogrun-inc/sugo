import http.server
import socketserver
import sugo


with socketserver.TCPServer(('127.0.0.1', 8000),
                            http.server.SimpleHTTPRequestHandler) \
                            as httpd:httpd.serve_forever()


