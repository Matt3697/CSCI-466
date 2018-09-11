import sys
portNum = sys.argv[1]
fileName = sys.argv[2]
file = open(fileName,"r")
print "This is the port number", portNum
print "This is the game board"
for line in file:
    print line
file.close()
print "End of script."
