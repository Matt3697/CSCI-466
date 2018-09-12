import sys
import httplib
import socket

portNum  = sys.argv[1] #port number
fileName = sys.argv[2] #file name for game board

file = open(fileName,"r")

print "This is the port number", portNum
print "This is the game board:"
for line in file: #print each line of the board
    print line
file.close()

#socket handling
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 1025))
s.listen(1)

print "End of script."
