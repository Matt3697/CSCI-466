#
#Authors: Matthew Sagen & Cory Petersen
#Date:    09/07/18
#
#server.py sets up an HTTP server used for recieving shots fired
#by an opponent in Battleship.
#

import sys

import numpy
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl
from numpy import savetxt
import codecs

arg_length = len(sys.argv)
port    = sys.argv[1]
portNum = int(port)
board_arr = [['_' for x in range(10)] for y in range(10)]
sunk_ships = []

class RequestHandler(BaseHTTPRequestHandler):
    def sunk_ship(self, ship_identifier):
        flag = True
        for x in board_arr:
            for i in x:
                if( i == ship_identifier): #if we find a Character belonging to the ship still in the board
                    flag = False
        return flag

    def send_result(self, coordinates):
        y = int(coordinates['x'])
        x = int(coordinates['y'])
        if(x >= 10 or y >= 10): #if they fire out of bounds
            msg = "Not Found"
            self.send_response(404, msg)
            return
        if(board_arr[x][y] == 'C' or board_arr[x][y] == 'B' or board_arr[x][y] == 'R' or board_arr[x][y] == 'S' or board_arr[x][y]== 'D'):#if we hit a ship return hit=1
            msg = 'hit=1'
            ship_identity = board_arr[x][y]
            board_arr[x][y] = 'X' #mark the spot that has been hit
            if(self.sunk_ship(ship_identity) == True):#if we have sunk a ship
                msg = 'hit=1\&sink=' + ship_identity
                sunk_ships.append(ship_identity) #add ship to list of sunken ships
                if(len(sunk_ships) == 5):
                    msg = msg + '\g_o' #g_o: game over
                    self.send_response(200, msg)
                self.send_response(200,msg)
            else:
                self.send_response(200,msg)
        elif(board_arr[x][y] == '_'):#if we miss the boat return hit=0
            msg = 'hit=0'
            self.send_response(200,msg)
        elif(board_arr[x][y] == 'X'): #if we hit the same spot return HTTP Gone
            self.send_response(410)
        elif(x > 10 or y > 10):#if we hit out of bound return HTTP Not Found
            self.send_response(404)
        elif(x < 0 or y < 0):#lower bound check
            self.send_response(404)
        else:
            msg = "Something went very wrong."
            self.send_response(400)
        update_board()

    def do_GET(self):
        f = open('own_board.txt','rb')
        data = f.read()
        decodedata = data.decode('utf-8').replace('\n','<br>')
        the_data = decodedata.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(the_data)
        f.close()
        return

    def do_POST(self): #handle POST requests
        the_coordinates = self.get_coordinates()
        self.send_result(the_coordinates)
        self.end_headers()

    def get_coordinates(self): #extract the data that was sent into an array
        data = self.rfile.read(int(self.headers['Content-Length']))
        coordinates_arr = dict(parse_qsl(data))
        coordinates = {key.decode(): val.decode() for key, val in coordinates_arr.items()}
        return coordinates

def update_board(): #update the board after player move
    numpy.savetxt('own_board.txt', board_arr, fmt='%s')

def handle_board():#populate the board with the contents of own_board
    global board_arr
    with open("own_board.txt") as textFile:
        board_arr = [list(line.rstrip()) for line in textFile]
    return board_arr

def handle_args():#throw error and exit if arguments are incorrect.
    if (arg_length != 4):
        return False


def start_server():
    try:
        server_address = ('127.0.0.1', portNum)
        print("Starting server 127.0.0.1 on port " + port)
        httpd = HTTPServer(server_address, RequestHandler)
        httpd.serve_forever()
    except Exception as e:
        print(str(e))

def main():
    print ("Processing...")
    board_arr = handle_board() #open own_board.txt and populate matrix with contents
    for x in board_arr:
        print(x)
    start_server()
    print ("End of script.")

main()
