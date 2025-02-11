from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import mimetypes
import sys

PORT_NUMBER = 3300

class CustomError(Exception):
    def __init__(self, message):
        super().__init__(message)

def set_headers(self, status_code=200, headers=[]):
    self.send_response(status_code)
    self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS, POST")
    self.send_header("Access-Control-Allow-Origin", "*")
    self.send_header("Access-Control-Allow-Headers", "*")

    for header in headers:
        self.send_header(header[0], header[1])

    self.end_headers()

def return_error(self, msg=""):
    set_headers(self, 400, [("Content-type", "text/html")])
    err_msg = "ERROR: " + str(msg)
    self.wfile.write(err_msg.encode("utf-8"))

def respond_json(self, data):
    set_headers(self, 200, [("Content-type", "application/json")])
    self.wfile.write(json.dumps(data).encode("utf-8"))

def respond_file(self, file_path):
    if os.path.isfile(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)

        if not mime_type:
            mime_type = "application/octet-stream"

    set_headers(self, 200, [("Content-type", mime_type)])

    with open(file_path, "rb") as file:
        self.wfile.write(file.read())

class MyServer(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        set_headers(self, 200)
        return

    def do_POST(self):
        post_body = None
        post_body_json = None

        try:
            content_length = int(self.headers["Content-Length"])
            post_body = self.rfile.read(content_length).decode("utf-8")
            
            print('Received POST request with body:')
            print(post_body)

            post_body_json = json.loads(post_body)
            print('Received POST request with JSON body:')
            print(post_body_json)

        except json.JSONDecodeError:
            return_error(self, "Received request with invalid JSON, ignoring.")
            pass

        except Exception:
            return_error(self, "Received invalid request, ignoring.")
            return

        if self.path == "/info":
            respond_json(self, {"title": "Basic Python Server", "message": "Hello, this is a basic python server.", "pong": post_body_json or post_body})

        return

    def do_GET(self):
        file_path = self.path.lstrip("/")
        if os.path.isfile(file_path):
            respond_file(self, file_path)

        else:
            return_error(self, "File not found")

        return
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            PORT_NUMBER = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port:", PORT_NUMBER)
    else:
        print("No port number provided. Using default port:", PORT_NUMBER)

    myServer = HTTPServer(("", PORT_NUMBER), MyServer)

    try:
        print(f"Starting HTTP server on port {PORT_NUMBER}...")
        myServer.serve_forever()
    except KeyboardInterrupt:
        myServer.server_close()
        print("Stopped HTTP server...")