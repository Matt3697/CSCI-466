import network_3_0
import argparse
import time
from time import sleep
import hashlib
import sys
from socket import timeout

class Packet:
    # the number of bytes used to store packet length
    seq_num_S_length = 10
    length_S_length = 10
    # length of md5 checksum in hex
    checksum_length = 32

    def __init__(self, seq_num, msg_S):
        self.seq_num = seq_num
        self.msg_S = msg_S

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

    def is_ack_packet(self):
        if self.msg_S == '1' or self.msg_S == '0':
            return True
        return False

class RDT_3_0:
     # latest_Packet sequence number used in a packet
    seq_num = 0
    # buffer of bytes read from network
    byte_buffer = ''
    timeout = .3


    def __init__(self, role_S, server_S, port):
        self.network = network_3_0.NetworkLayer(role_S, server_S, port)

    def disconnect(self):
        self.network.disconnect()

    # rdt3.0 has the following features:
        # delivers data under no corruption or loss in the network and uses a modified Packet class to send ACKs
        # does not deliver corrupt packets and uses modified Packet class to send NAKs
        # resends data following a NAK
        # retransmits a lost packet after a timeout
        # retransmits a packet after a lost ACK
        # ignores a duplicate packet after a premature timeout (or after a lost ACK)

    def rdt_3_0_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        cur_seq = self.seq_num
        while cur_seq == self.seq_num:
            self.network.udt_send(p.get_byte_S())
            timer = time.time()
            resp = ''
            # Wait for ack or nak
            #while no response and no timeout, receive packet
            while resp == '' and timer + self.timeout > time.time():
                resp = self.network.udt_receive()

            if resp == '':
                continue

            msg_length = int(resp[:Packet.length_S_length])
            self.byte_buffer = resp[msg_length:]

            if not Packet.corrupt(resp[:msg_length]):
                resp_packet = Packet.from_byte_S(resp[:msg_length])
                if resp_packet.seq_num < self.seq_num:
                    # trying to send duplicate packet
                    print("duplicate packet detected.")
                    test_Packet = Packet(resp_packet.seq_num, "1")
                    self.network.udt_send(test_Packet.get_byte_S())
                elif resp_packet.msg_S is "1":
                    print("Sender Received ACK, move on to next packet.")
                    # Sender Incrementing seq_num)
                    self.seq_num += 1
                elif resp_packet.msg_S is "0":
                    print("Sender: NAK received")
                    self.byte_buffer = ''
            else:
                # else sender recieved Corrupted ACK"
                self.byte_buffer = ''


    def rdt_3_0_receive(self):
        #ignore duplicate packets
        #receiver specifies seq_num of ACKed packet
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S
        cur_seq = self.seq_num
        # Don't move on until seq_num has been updated
        # keep extracting packets - if reordered, could get more than one
        while cur_seq == self.seq_num:
            # check if we have received enough bytes
            if len(self.byte_buffer) < Packet.length_S_length:
                break  # not enough bytes to read packet length
            # extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                break  # not enough bytes to read the whole packet

            # Check if the packet is corrupt
            if Packet.corrupt(self.byte_buffer):
                # Send a NAK
                print("Reciever: Corrupt packet found. send a NAK")
                ans_Packet = Packet(self.seq_num, "0")
                self.network.udt_send(ans_Packet.get_byte_S())
            else:
                # create packet from buffer content
                p = Packet.from_byte_S(self.byte_buffer[0:length])
                # Check packet to see if it as an acknowledgement packet
                if p.is_ack_packet():
                    self.byte_buffer = self.byte_buffer[length:]
                    continue
                if p.seq_num < self.seq_num:
                    print("Reciever already received this packet, ACK again.")
                    ans_Packet = Packet(p.seq_num, "1")
                    self.network.udt_send(ans_Packet.get_byte_S())
                elif p.seq_num == self.seq_num:
                    print("Reciever got new packet. Send ACK and increment seq_num")
                    ans_Packet = Packet(self.seq_num, "1")
                    self.network.udt_send(ans_Packet.get_byte_S())
                    #Reciever increments seq_num
                    self.seq_num += 1
                # Add contents to return string
                ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S
            # remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            # if this was the last packet, will return on the next iteration
        return ret_S


    # return true if a packet is a nak.
    def isNAK(self, resp):
        if resp is "NAK":
            return True
        else:
            return False

    # return true if packet is an ack.
    def isACK(self, resp):
        if(resp == 1):
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
        rdt.rdt_2_1_send('MSG_FROM_CLIENT')
        sleep(2)
        print(rdt.rdt_3_0_receive())
        rdt.disconnect()
    else:
        sleep(1)
        print(rdt.rdt_3_0_receive())
        rdt.rdt_2_1_send('MSG_FROM_SERVER')
        rdt.disconnect()
