#
#Authors: Matthew Sagen & Cory Petersen
#Date:    09/07/18
#
#server.py sets up an HTTP server used for sending/recieving shots fired
#by an opponent in Battleship.
#

import sys
#import httplib
import socket
from http.server import HTTPServer

arg_length = len(sys.argv)

class requests():
    def on_POST():
        print("Success")

def throw_argument_error():
    print ("Error: incorrect arguments.")
    sys.exit(1)

def handle_args():
    if (arg_length != 3):
        throw_argument_error()
    else:
        portNum    = sys.argv[1]  #port number
        portNum    = int(portNum) #convert port number to an integer
        fileName   = sys.argv[2]  #file name for game board

def start_server():
    httpd = HTTPServer(serv_address, handleRequests)
    httpd.serve_forever()


def main():
    print ("Beggining.")
    handle_args() #make sure arguments are valid
    #start_server()
    #conn.close()
    #s.close()
    print ("End of script.")
