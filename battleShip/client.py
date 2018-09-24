#
#Authors: Matthew Sagen & Cory Petersen
#Date:    09/07/18
#
#client.py sets up an HTTP client used for sending shots fired
#by an opponent in Battleship.
#
import sys
import numpy
import requests
from urllib.parse import parse_qsl
from numpy import savetxt
import re

ipAdd      = sys.argv[1]  #IP Address
portNum    = sys.argv[2]  #port number
x          = sys.argv[3]  #x coordinate
y          = sys.argv[4]  #y coordinate
i          = 0
sunk_ships = ['_','_','_','_','_']
opp_board_arr = [['_' for x in range(10)] for y in range(10)]

def handle_args():
    if(len(sys.argv) != 5):
        print ("Error: incorrect arguments. Try python3 server.py <ip_address> <port_number> <xCoordinate> <yCoordinate>")
    else:
        search_ip = re.search('[0-9]{3}\.[0-9]\.[0-9]\.[0-9]', sys.argv[1])#search for a formatted ip_address
        search_ip = str(search_ip)
        search_portNum = re.search('[0-9]+', sys.argv[2]) #search for a formatted port Number
        search_portNum = str(search_portNum)
        search_x = re.search('[0-9]', sys.argv[3])
        search_x = str(search_x)
        search_y = re.search('[0-9]', sys.argv[4])
        search_y = str(search_y)
        if(search_ip == 'None'): #'[0-9]{3}\.[0-9]\.\[0-9]\.\[0-9]'), argv[1]):
            print("Error: Please enter a valid IP address.")
            return False
        elif(search_portNum == 'None'):
            print("Error: Please enter a valid Port Number.")
            return False
        elif(search_x == 'None'):
            print("Error: Please enter a valid X coordinate. (0-9)")
            return False
        elif(search_y == 'None'):
            print("Error: Please enter a valid Y coordinate. (0-9)")
            return False
        else:
            return True

def reset_board(): #reset the board after a game has finished
    opp_board_arr = [['_' for x in range(10)] for y in range(10)]
    numpy.savetxt('opp_board.txt', opp_board_arr, fmt='%s')

def process_result(reason):
    reason_len = len(reason)
    sub_reason = reason[reason_len - 1]
    if(reason == "hit=1" or reason == "hit=1\&sink=D" or reason == "hit=1\&sink=C" or reason == "hit=1\&sink=S" or reason == "hit=1\&sink=B" or reason == "hit=1\&sink=R" or sub_reason == 'o'): #update opp_board with an X at the coordinates that we fire at
        if(sub_reason == 'D' or sub_reason == 'C' or sub_reason == 'S' or sub_reason == 'B' or sub_reason == 'R'):
            print("You've hit and sank ship " + sub_reason + "!")
        elif(sub_reason == 'o'):
            print("You've won the game!")
            opp_board_arr[int(y)][int(x)] = 'X'
            for i in opp_board_arr:
                print(i)
            reset_board()
            return
        opp_board_arr[int(y)][int(x)] = 'X'
    elif(reason == "Gone"): #don't update the board if we already fired at that spot
        return
    elif(reason == "hit=0"): #if we miss update board with a O
        opp_board_arr[int(y)][int(x)] = 'O'
    numpy.savetxt('opp_board.txt', opp_board_arr, fmt='%s')
    for i in opp_board_arr:
        print(i)

def server_connection(): #function to send a fire post request to the server.
    newAddress = 'http://' + ipAdd + ':' + portNum
    print("Firing at " + newAddress + " at x=" + x + "&y=" + y)
    payload = {'x':x, 'y':y}
    r = requests.post(newAddress, data=payload)#the fire message
    print(r.status_code, r.reason)
    process_result(r.reason)

def handle_board():#populate the board with the contents of opp_board
    global opp_board_arr
    with open("opp_board.txt") as textFile:
        opp_board_arr = [line.split() for line in textFile]
    return opp_board_arr

def main():
    print ("Processing...")
    opp_board_arr = handle_board()
    if(not handle_args()):       #make sure arguments are valid
        sys.exit()
    else:
        server_connection() #create connection with server
    print ("End of turn.")

main()
