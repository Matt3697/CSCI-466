import sys
import socket
import httplib

#ipAdd    = sys.argv[1] #IP Address
portNum  = sys.argv[1] #port number
portNum  = int(portNum)
x        = sys.argv[2] #x coordinate
y        = sys.argv[3] #y coordinate


#host = socket.gethostname()

#msg = "http://" + host + str(portNum) + "?x=" + x + "&y=" + y

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((host, portNum))
#s.send(bytes('Hola'))
#data = conn.recv(1024)
#get data such as own_board & opp_board from server
#http://111.222.333.444:5555?x=5&y=7
#s.close()
