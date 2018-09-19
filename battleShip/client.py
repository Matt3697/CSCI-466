#
#Authors: Matthew Sagen & Cory Petersen
#Date:    09/07/18
#
#client.py sets up an HTTP client used for sending shots fired
#by an opponent in Battleship.
#
import sys
#import http.client
import requests

ipAdd      = sys.argv[1]  #IP Address
portNum    = sys.argv[2]  #port number
x          = sys.argv[3]  #x coordinate
y          = sys.argv[4]  #y coordinate

def throw_argument_error():
    print ("Error: incorrect arguments. Try python3 server.py <ip_address> <port_number> <xCoordinate> <yCoordinate>")
    sys.exit(0)

def handle_args():
    if(len(sys.argv) != 5):
        throw_argument_error()

def client_connection():
    try:
        #payload = {'key1': 'value1', 'key2': 'value2'}
        newAddress = 'http://' + ipAdd + ':' + portNum #+ '?x=' + x + '&y=' + y #concatonate ip address w/ the port number and x/y coordinates
        print("Connecting to " + newAddress)
        payload = {'x':x, 'y':y}
        r = requests.post(newAddress, data=payload)
        r.status_code
        print(r.text)
        #connection = http.client.HTTPConnection(ipAdd) #get conneciton to other system
        #connection.connect()
        #connection.request("POST", newAddress, params, headers={})
        #response = connection.getresponse()    #get the response
        #print(response.status, response.reason)
        #r = response.read()
        #print (r)
        #connection.close()
    except Exception as e:
        print(str(e))

def main():
    print ("Processing...")
    handle_args()       #make sure arguments are valid
    client_connection() #create connection with server
    print ("End of script.")

main()
