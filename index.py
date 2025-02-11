from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import mimetypes

PORT_NUMBER = 3300

class CustomError(Exception):
    def __init__(self, message):
        super().__init__(message)


def return_error(self, msg=""):
    self.send_response(400)
    self.send_header("Content-type", "text/html")
    self.send_header("Access-Control-Allow-Origin", "*")
    self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS, POST")
    self.send_header("Access-Control-Allow-Headers", "*")
    self.end_headers()
    err_msg = "ERROR: " + str(msg)
    self.wfile.write(err_msg.encode("utf-8"))


def respond_json(self, data):
    self.wfile.write(json.dumps(data).encode("utf-8"))

def respond_file(self, file_path):
    with open(file_path, "rb") as file:
        self.wfile.write(file.read())

class MyServer(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

        return

    def do_POST(self):
        try:
            content_length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(content_length).decode("utf-8"))
            print(body)

        except json.JSONDecodeError:
            return_error(self, "Received request with invalid JSON, ignoring.")
            return

        except Exception:
            return_error(self, "Received invalid request, ignoring.")
            return

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

        if self.path == "/info":
            respond_json(self, {"title": "Basic Python Server", "message": "Hello, this is a basic python server."})

        return

    def do_GET(self):

        file_path = self.path.lstrip("/")
        if os.path.isfile(file_path):

            self.send_response(200)

            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET")
            self.send_header("Access-Control-Allow-Headers", "*")

            mime_type, _ = mimetypes.guess_type(file_path)

            if mime_type:
                self.send_header("Content-type", mime_type)
            else:
                self.send_header("Content-type", "application/octet-stream")

            self.end_headers()

            respond_file(self, file_path)

        else:
            return_error(self, "File not found")

        return
    
myServer = HTTPServer(("", PORT_NUMBER), MyServer)

try:
    print("starting http server...")
    myServer.serve_forever()
except KeyboardInterrupt:
    myServer.server_close()
    print("stopped http server...")
