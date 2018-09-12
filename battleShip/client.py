import sys
import socket
import httplib

#ipAdd    = sys.argv[1] #IP Address
portNum  = sys.argv[1] #port number
portNum  = int(portNum)
#x        = sys.argv[3] #x coordinate
#y        = sys.argv[4] #y coordinate

#print "This is the IP Address:", ipAdd
print "This is the port number:", portNum
#print "This is the x coordinate:", x
#print "This is the y coordinate:", y

host = socket.gethostname()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, portNum))
s.send(bytes('Hello'))
#data = conn.recv(1024)
s.close()
