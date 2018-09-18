#
#Authors: Matthew Sagen & Cory Petersen
#Date:    09/07/18
#
#server.py sets up an HTTP server used for recieving shots fired
#by an opponent in Battleship.
#

import sys
import http.client
import urllib.request
#from http.server import HTTPServer

arg_length = len(sys.argv)
portNum    = 0


def throw_argument_error():
    print ("Error: incorrect arguments. Try python3 server.py <port_number> <file_name>")
    sys.exit(0)

def handle_args():
    if (arg_length != 3):
        throw_argument_error()
    else:
        portNum    = sys.argv[1]  #port number
        portNum    = int(portNum) #convert port number to an integer
        fileName   = sys.argv[2]  #file name for game board

def start_server():
    #values = {''}
    #data = urllib.parse.urlencode(values)
    #data = data.encode('utf-8')
    #req = urllib.request.Request(url,data)
    #resp = urllib.request.urlopen(req)
    #respData = resp.read()
    #print (respData)
    try:
        connection = http.client.HTTPConnection("www.google.com")
        connection.request("GET", "/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png")
        #data = urllib.request.urlopen('https://www.google.com/search?q=test')
        response = connection.getresponse()
        r = response.read()
        print (r)
        connection.close()
    except Exception as e:
        print(str(e))


def main():
    print ("Processing...")
    handle_args()  #make sure arguments are valid
    start_server() #create connection with server
    print ("End of script.")

main()
