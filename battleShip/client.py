import sys
import socket
import httplib

#ipAdd    = sys.argv[1] #IP Address
portNum  = sys.argv[1] #port number
portNum  = int(portNum)
x        = sys.argv[2] #x coordinate
y        = sys.argv[3] #y coordinate

#print "This is the IP Address:", ipAdd
print "This is the port number:", portNum
#print "This is the x coordinate:", x
#print "This is the y coordinate:", y

host = socket.gethostname()

#msg = "http://" + host + str(portNum) + "?x=" + x + "&y=" + y

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, portNum))
s.send(bytes('Hola'))
#data = conn.recv(1024)
#get data such as own_board & opp_board from server
#http://111.222.333.444:5555?x=5&y=7
s.close()
