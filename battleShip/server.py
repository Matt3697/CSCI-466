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

arg_length = len(sys.argv)
portNum    = 0

class HandleRequests(BaseHTTPRequestHandler):
    def do_POST(self):
        coordinates = self.get_coordinates()
        self.send_response(200)
        self.end_headers()
        # need to check here if the spot on the board gets hit

    def do_GET(self):
        self.send_response(404)
        self.end_headers()

    def get_coordinates(self):
        raw_data = self.rfile.read(int(self.headers['Content-Length']))
        byte_coordinates = dict(parse_qsl(raw_data))
        string_coordinates = {key.decode(): val.decode() for key, val in byte_coordinates.items()} #convert from bytes to str
        return string_coordinates

def throw_argument_error():
    print ("Error: incorrect arguments. Try python3 server.py <port_number> <file_name>")
    sys.exit(0)

def handle_args():
    if (arg_length != 3):
        throw_argument_error()
    else:
        portNum    = sys.argv[1]  #port number
        portNum    = int(portNum) #convert port number to an integer
        fileName   = sys.argv[2]  #file name for game board

def start_server(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    try:
        server_address = ('', portNum)
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()

    except Exception as e:
        print(str(e))


def main():
    print ("Processing...")
    handle_args()  #make sure arguments are valid
    start_server() #create connection with server
    print ("End of script.")

main()
