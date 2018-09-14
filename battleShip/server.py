import sys
import httplib
import socket
from http.server import HTTPServer

portNum  = sys.argv[1] #port number
portNum  = int(portNum) #convert port number to an integer
fileName = sys.argv[2] #file name for game board
host     = socket.gethostname()
arg_length = len(sys.argv)

class requests():
    def on_POST():
        print("Success")

def throw_argument_error():
    print ("Error: incorrect arguments.")

def handle_args():
    print type(arg_length)
    if arg_length != 3:
        throw_argument_error()
#def socket_handling()
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.bind((host, portNum))
    #serv_address = (host, portNum)
    #s.listen(1)

def start_server():
    httpd = HTTPServer(serv_address, handleRequests)
    httpd.serve_forever()

#conn, addr = s.accept()
#data = conn.recv(BUFFER_SIZE)
#conn.send(data)
#print('Got connection from ', addr[0], '(', addr[1], ')')
#print(conn.recv(1024))
#file = open(fileName,"r")
#file.close()


def main():
    handle_args() #make sure arguments are valid
    start_server()
    conn.close()
    s.close()
    print ("End of script.")
