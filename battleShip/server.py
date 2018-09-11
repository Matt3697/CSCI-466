import sys

portNum  = sys.argv[1] #port number
fileName = sys.argv[2] #file name for game board

file = open(fileName,"r")

print "This is the port number", portNum
print "This is the game board"

for line in file: #print each line of the board
    print line
file.close()
print "End of script."
