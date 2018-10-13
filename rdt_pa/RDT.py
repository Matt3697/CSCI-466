import Network
import argparse
from time import sleep
import hashlib
import sys

class Packet:
    # the number of bytes used to store packet length
    seq_num_S_length = 10
    length_S_length = 10
    # length of md5 checksum in hex
    checksum_length = 32
    # type of Packet

    def __init__(self, seq_num, msg_S, ack=None):
        self.seq_num = seq_num
        self.msg_S = msg_S
        self.ack = ack

    @classmethod
    def from_byte_S(self, byte_S):
        if Packet.corrupt(byte_S):
            raise RuntimeError('Cannot initialize Packet: byte_S is corrupt')
        # extract the fields
        seq_num = int(byte_S[Packet.length_S_length: Packet.length_S_length+Packet.seq_num_S_length])
        msg_S = byte_S[Packet.length_S_length+Packet.seq_num_S_length+Packet.checksum_length :]
        return self(seq_num, msg_S)

    def get_byte_S(self):
        # convert sequence number of a byte field of seq_num_S_length bytes
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        # convert length to a byte field of length_S_length bytes
        length_S = str(self.length_S_length + len(seq_num_S) + self.checksum_length + len(self.msg_S)).zfill(self.length_S_length)
        # compute the checksum
        checksum = hashlib.md5((length_S+seq_num_S+self.msg_S).encode('utf-8'))
        checksum_S = checksum.hexdigest()
        # compile into a string
        return length_S + seq_num_S + checksum_S + self.msg_S

    @staticmethod
    def corrupt(byte_S):
        # extract the fields
        length_S = byte_S[0:Packet.length_S_length]
        seq_num_S = byte_S[Packet.length_S_length : Packet.seq_num_S_length+Packet.seq_num_S_length]
        checksum_S = byte_S[Packet.seq_num_S_length+Packet.seq_num_S_length : Packet.seq_num_S_length+Packet.length_S_length+Packet.checksum_length]
        msg_S = byte_S[Packet.seq_num_S_length+Packet.seq_num_S_length+Packet.checksum_length :]

        # compute the checksum locally
        checksum = hashlib.md5(str(length_S+seq_num_S+msg_S).encode('utf-8'))
        computed_checksum_S = checksum.hexdigest()
        # and check if the same
        return checksum_S != computed_checksum_S


class RDT:
    # latest sequence number used in a packet
    seq_num = 1
    # buffer of bytes read from network
    byte_buffer = ''

    def __init__(self, role_S, server_S, port):
        self.network = Network.NetworkLayer(role_S, server_S, port)

    def disconnect(self):
        self.network.disconnect()

    def rdt_1_0_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        self.seq_num += 1
        self.network.udt_send(p.get_byte_S())

    def rdt_1_0_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S
        #keep extracting packets - if reordered, could get more than one
        while True:
            #check if we have received enough bytes
            if(len(self.byte_buffer) < Packet.length_S_length):
                return ret_S #not enough bytes to read packet length
            #extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S #not enough bytes to read the whole packet
            #create packet from buffer content and add to return string
            p = Packet.from_byte_S(self.byte_buffer[0:length])
            ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S
            #remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            #if this was the last packet, will return on the next iteration

    # rdt2.1 has the following features:
        # delivers data under no corruption in the network
        # uses a modified Packet class to send ACKs
        # does not deliver corrupt packets
        # uses modified Packet class to send NAKs for corrupt packets
        # resends data following a NAK

    def rdt_2_1_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        while True:
            r = ""
            # send to receiver over udt
            self.network.udt_send(p.get_byte_S())

            # try to get response from receiver
            while(r == ""):
                r = self.network.udt_receive()
            # extract information from response
            length = int(r[:Packet.length_S_length])
            packet_info = Packet.from_byte_S(r[:length])
            response = packet_info.msg_S
            print(response + '<--- MESSAGE')
            # check type of response
            if(self.isNAK(response)):
            elif(self.isACK(response)):
                self.seq_num += 1
                break

    def rdt_2_1_receive(self):#
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S

        while True:
            # check if we have received enough bytes
            if(len(self.byte_buffer) < Packet.length_S_length):
                # not enough bytes to read packet length
                return ret_S
            # extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                # not enough bytes to read the whole packet
                return ret_S
            # check if the packet is corrupted
            if(self.isCorrupted(self.byte_buffer)):
                nak = Packet(self.seq_num, "0") #send which packet is corrupted
                self.network.udt_send(nak.get_byte_S())
                break

            else:
                #extract the data from the packet and put into ret_S
                p = Packet.from_byte_S(self.byte_buffer[0:length])
                nak = Packet(self.seq_num, "1") #send which packet is corrupted
                self.network.udt_send(nak.get_byte_S())
                ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S
                #remove the packet bytes from the buffer
                self.byte_buffer = self.byte_buffer[length:]
                #if this was the last packet, will return on the next iteration


    # rdt3.0 has the following features:
        # delivers data under no corruption or loss in the network and uses a modified Packet class to send ACKs
        # does not deliver corrupt packets and uses modified Packet class to send NAKs
        # resends data following a NAK
        # retransmits a lost packet after a timeout
        # retransmits a packet after a lost ACK
        # ignores a duplicate packet after a premature timeout (or after a lost ACK)

    def rdt_3_0_send(self, msg_S):
        # acknowledgement packet
        # receive ACK before sending next packet
        # if NAK send duplicate packet
        # 0 - new packet 1 - retransmission
        # handle packet loss: Sender waits reasonable amount of time, retransmit if no ACK received in this time.
        p = Packet(self.seq_num, msg_S)
        timeout = 2
        while True:
            time_of_last_data = time.time()
            self.network.udt_send(p.get_byte_S())
            r = None
            while r == None:
                r = self.rdt_2_0_receive()
            if r != "N":
                return
            elif time_of_last_data + timeout < time.time():
                return
        pass

    def rdt_3_0_receive(self):
        #ignore duplicate packets
        #receiver specifies seq_num of ACKed packet

        pass

    def corrupt():
        pass

 # check if the packet contains a NAK response
    def isNAK(self, response):
        if(response == 0):
            return True
        else:
            return False

    # check if the packet contains an ACK response
    def isACK(self, response):
        if(response == 1):
            print("yo")
            return True
        else:
            return False

    # check if the packet is corrupted
    def isCorrupted(self, packet):
        if(Packet.corrupt(packet)):
            return True
        else:
            return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RDT implementation.')
    parser.add_argument('role', help='Role is either client or server.', choices=['client', 'server'])
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    rdt = RDT(args.role, args.server, args.port)
    if args.role == 'client':
        rdt.rdt_1_0_send('MSG_FROM_CLIENT')
        sleep(2)
        print(rdt.rdt_1_0_receive())
        rdt.disconnect()
    else:
        sleep(1)
        print(rdt.rdt_1_0_receive())
        rdt.rdt_1_0_send('MSG_FROM_SERVER')
        rdt.disconnect()
