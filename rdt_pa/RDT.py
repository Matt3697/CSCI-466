import Network
import argparse
import time
from time import sleep
import hashlib
import sys

class Packet:
    # the number of bytes used to store packet length
    seq_num_S_length = 10
    length_S_length = 10
    # length of md5 checksum in hex
    checksum_length = 32

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
        byte_s = p.get_byte_S()
        #print('Sending Packet')
        while True:
            self.network.udt_send(byte_s)
            # wait for ACK or NAK

            pack_ack = self.receive_packet()
			# Break if successfully sent, otherwise retry

            corrupt = Packet.corrupt(pack_ack.get_byte_S())

            print(pack_ack.msg_S)

            if not corrupt and pack_ack.msg_S == 'ACK':
                self.seq_num = 1 - self.seq_num
                #print('Packet successfully sent')

                break
			# self.byte_buffer = ''


        '''
        p = Packet(self.seq_num, msg_S)
        i = 0
        while True:
            # send to receiver over udt
            # try to get nak/ack response from receiver
            r = self.network.udt_receive()
            while True:
                #check if we have received enough bytes
                if(len(self.byte_buffer) < Packet.length_S_length):
                    break #not enough bytes to read packet length
                #extract length of packet
                length = int(self.byte_buffer[:Packet.length_S_length])
                if len(self.byte_buffer) < length:
                    break #not enough bytes to read the whole packet
                #create packet from buffer content
                r = Packet.from_byte_S(self.byte_buffer[0:length])
                #remove the packet bytes from the buffer
                self.byte_buffer = self.byte_buffer[length:]
                #if this was the last packet, will return on the next iteration
            print(r)
            # response = int(response)
            # check type of response
            if r.ack == "NAK":
                print("NAK received.")
                self.network.udt_send(p.get_byte_S())
                continue
            #increase the seq_num if an ack is recieved
            elif r.ack == "ACK":
                print("ACK received.")
                self.seq_num += 1
                break
            else:
                print("Nak or Ack corrupt.")
            '''

    def rdt_2_1_receive(self):
        resp = Packet(self.seq_num, 'ACK')
        self.network.udt_send(resp.get_byte_S())
        p = self.receive_packet()
        corrupt = Packet.corrupt(p.get_byte_S())

        if not corrupt and p.seq_num == self.seq_num:
            #print('Sending ACK')
            resp = Packet(self.seq_num, 'ACK')
            self.network.udt_send(resp.get_byte_S())
            self.seq_num = 1 - self.seq_num
            return p.msg_S

        else:
            #print('Sending NAK')
            resp = Packet(self.seq_num, 'NAK')
            self.network.udt_send(resp.get_byte_S())
            return self.rdt_2_1_receive()

        '''
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
            # check if packet is corrupt
            if(self.isCorrupted(self.byte_buffer)):
                print("The Packet is corrupt.")
                nak = Packet(self.seq_num, "0", "NAK") #send which packet is corrupted
                self.network.udt_send(nak.get_byte_S())
                break

            else:
                #extract the data from the packet and put into ret_S
                p = Packet.from_byte_S(self.byte_buffer[0:length])

                print("The Packet is correct.")
                ack = Packet(self.seq_num, "1", "ACK")
                self.network.udt_send(ack.get_byte_S())

                ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S
                #remove the packet bytes from the buffer
                self.byte_buffer = self.byte_buffer[length:]
                #if this was the last packet, will return on the next iteration

    '''
    # rdt3.0 has the following features:
        # delivers data under no corruption or loss in the network and uses a modified Packet class to send ACKs
        # does not deliver corrupt packets and uses modified Packet class to send NAKs
        # resends data following a NAK
        # retransmits a lost packet after a timeout
        # retransmits a packet after a lost ACK
        # ignores a duplicate packet after a premature timeout (or after a lost ACK)

    def rdt_3_0_send(self, msg_S):
        self.seq_num = 1 - self.seq_num
        p = Packet(self.seq_num, msg_S)
        byte_s = p.get_byte_S()
        while True:
        	print('Sending Packet')
        	self.network.udt_send(byte_s)

        	# wait for ACK or NAK
        	ack = ''
        	time_wait = time.time()
        	while ack == '' and time.time() - time_wait > 1:
        		ack = self.network.udt_receive()
        	# Get packet from bytes and check if corrupt
        	corrupt = False
        	try:
        		pack_ack = from_bytes_S(ack)
        	except RuntimeError:
        		print('Corrupt ACK or NAK. Attempting Transmission again...')
        		corrupt = True
        	# Break if successfully sent, otherwise retry
        	if ack != '' and not corrupt and pack_ack.seq_num == seq_num and pack_ack.msg_S == 'ACK':
        		print('Packet successfully sent')
        		return

    def rdt_3_0_receive(self):
        #ignore duplicate packets
        #receiver specifies seq_num of ACKed packet
        resp = Packet(self.seq_num, 'ACK')
        self.network.udt_send(resp.get_byte_S())
        p = self.receive_packet()
        corrupt = Packet.corrupt(p.get_byte_S())

        if not corrupt and p.seq_num == self.seq_num:
            #print('Sending ACK')
            resp = Packet(self.seq_num, 'ACK')
            self.network.udt_send(resp.get_byte_S())
            self.seq_num = 1 - self.seq_num
            return p.msg_S

        elif corrupt:
            #print('Sending NAK')
            resp = Packet(self.seq_num, 'NAK')
            self.network.udt_send(resp.get_byte_S())
            return self.rdt_3_0_receive()

        elif p.seq_num > self.seq_num: #not totally sure on the logic here
            print("duplicate packet")
            return


    # check if packet contains a NAK
    def isNAK(self, response):
        if response is "NAK":
            return True
        else:
            return False

    # check if packet contains an ACK
    def isACK(self, response):
        if(response == 1):
            return True
        else:
            return False

    # check if packet is corrupt
    def isCorrupted(self, packet):
        if(Packet.corrupt(packet)):
            return True
        else:
            return False

    def receive_packet(self):
    	#print('Receiving Packet')
    	while True:
    		p = None
    		byte_S = self.network.udt_receive()
    		self.byte_buffer += byte_S

    		if(len(self.byte_buffer) >= Packet.length_S_length):
    			#extract length of packet
    			length = int(self.byte_buffer[:Packet.length_S_length])
    			if len(self.byte_buffer) >= length:
    				# Checks if packet received is corrupt
    				try:
    					p = Packet.from_byte_S(self.byte_buffer[:length])
    					self.byte_buffer = self.byte_buffer[length:]
    				except RuntimeError:
    					#print('corrupt packet')
    					self.byte_buffer = self.byte_buffer[length:]
    		if p != None:
    			return p

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
