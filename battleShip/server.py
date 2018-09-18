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
