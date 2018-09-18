#
#Authors: Matthew Sagen & Cory Petersen
#Date:    09/07/18
#
#client.py sets up an HTTP client used for sending shots fired
#by an opponent in Battleship.
#
import sys
import http.client

#ipAdd    = sys.argv[1] #IP Address
portNum  = sys.argv[1] #port number
portNum  = int(portNum)
x        = sys.argv[2] #x coordinate
y        = sys.argv[3] #y coordinate


def handle_args():
    if (arg_length != 4):
        throw_argument_error()
    else:
        portNum    = sys.argv[1]  #port number
        portNum    = int(portNum) #convert port number to an integer
        x          = int(sys.argv[2])  #x coordinate
        y          = int(sys.argv[3])  #y coordinate

def client_connection():
    try:
        connection = http.client.HTTPConnection("www.google.com")
        connection.request("GET", "/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png")
        response = connection.getresponse()
        r = response.read()
        print (r)
        connection.close()
    except Exception as e:
        print(str(e))

def main():
    print ("Processing...")
    handle_args()       #make sure arguments are valid
    client_connection() #create connection with server
    print ("End of script.")

main()
