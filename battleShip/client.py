#
#Authors: Matthew Sagen & Cory Petersen
#Date:    09/07/18
#
#client.py sets up an HTTP client used for sending shots fired
#by an opponent in Battleship.
#
import sys
import http.client


def handle_args():
    if (arg_length != 5):
        throw_argument_error()
    else:
        ipAdd    = sys.argv[1] #IP Address
        portNum    = sys.argv[2]  #port number
        portNum    = int(portNum) #convert port number to an integer
        x          = int(sys.argv[3])  #x coordinate
        y          = int(sys.argv[4])  #y coordinate

def client_connection():
    try:
        connection = http.client.HTTPConnection(ipAdd) #get conneciton to other system
        newAddress = 'http://' + ipAdd + ':' + portNum + '?x=' + x + '&y=' + y #concatonate ip address w/ the port number and x/y coordinates
        connection.request("POST", newAddress) #request a post to the new address
        response = connection.getresponse()    #get the response
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
