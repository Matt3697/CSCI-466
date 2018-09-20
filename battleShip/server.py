#
#Authors: Matthew Sagen & Cory Petersen
#Date:    09/07/18
#
#server.py sets up an HTTP server used for recieving shots fired
#by an opponent in Battleship.
#

import sys
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl

def stop_server():
    httpd.close_connection()

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        coordinates = self.get_coordinates()
        print(coordinates)
        self.send_response(200)
        self.end_headers()
        # check here if the spot on the board gets hit

    def get_coordinates(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        byte_coordinates = dict(parse_qsl(data))
        string_coordinates = {key.decode(): val.decode() for key, val in byte_coordinates.items()} #convert from bytes to str
        return string_coordinates

arg_length = len(sys.argv)
port    = sys.argv[1]
portNum = int(port)

def throw_argument_error():
    print ("Error: incorrect arguments. Try python3 server.py <port_number> <file_name>")
    sys.exit(0)

def handle_args():
    if (arg_length != 3):
        throw_argument_error()

def start_server():
    try:
        server_address = ('127.0.0.1', portNum)
        print("Starting server 127.0.0.1 on port " + port)
        httpd = HTTPServer(server_address, RequestHandler)
        httpd.serve_forever()
    except Exception as e:
        print(str(e))


def main():
    print ("Processing...")
    handle_args()  #make sure arguments are valid
    start_server()
    print ("End of script.")

main()
