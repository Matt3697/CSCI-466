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

def handle_board(file):
    

class RequestHandler(BaseHTTPRequestHandler):

    def send_response(coordinates):
        #if we hit a boat return hit=1
            #if we sink return hit=1 sink=(c,b,r,s,or d)
        #if we miss the boat return hit=0
        #if we hit the same spot return HTTP Gone
        #if we hit out of bound return HTTP Not Found
        #if format is bad return HTTP Bad Request

    def do_POST(self):
        coordinates = self.get_coordinates()
        #print(coordinates)
        self.send_response(coordinates)
        self.end_headers()

    def get_coordinates(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        byte_coordinates = dict(parse_qsl(data))
        string_coordinates = {key.decode(): val.decode() for key, val in byte_coordinates.items()}
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
    handle_board() #open own_board.txt and populate matrix with contents
    start_server()
    print ("End of script.")

main()
