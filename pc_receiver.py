# plan here is to write python code that will recieve the sockets sent from the pynq and then.
# if that is able to recieve quickly then we can use that in the controller.py file to actually
# create a nice bit of software.

import sys
from socket import *
import threading
import time
from collections import defaultdict
import heapq

# Receive address
ROUTER_PORT = 1300
HOST = '127.0.0.1'

# Send address
ROUTER_PORT2 = 1200
HOST2 = '127.0.0.1'

# --------------------------------------------------------------------------------------------------------- #

data_received = []
num_peripherals = 0

# routing_table = []
# sent_packets = []
# last_heard = []
# router_list = []

# --------------------------------------------------------------------------------------------------------- #

def receive_from_pynq():
    global data_received

    # set up listening sockets
    s_sock = socket(AF_INET, SOCK_DGRAM)
    address = (HOST2, ROUTER_PORT2)
    s_sock.bind(address)
    print(f'Listening on port:{ROUTER_PORT2}')

    # proccess data this is not write just very placeholder
    while True:
        msg, c_add = s_sock.recvfrom(1024)
        decoded_lsp = msg.decode()
        print(f"\n+received {decoded_lsp}")

        data_received.append(decoded_lsp)

# --------------------------------------------------------------------------------------------------------- #

# this is code for the pynq probably that is sending packets, however can be used here to send
# information for control actually (may or may not work). Again just copied my own old code
# will need restructuring to do what we want it to.
def send_instructions():
    c_sock = socket(AF_INET, SOCK_DGRAM)

    # should just send a packet with a random number that I type into command line
    while(True):
        input_command = input("")
        print("-sending",input_command)
        packet = input_command.encode()
        send_address = (HOST, ROUTER_PORT)
        c_sock.sendto(packet, send_address)

# --------------------------------------------------------------------------------------------------------- #

if __name__ == "__main__":

    # set up all threads that we want to exist
    recieve_data = threading.Thread(target=receive_from_pynq)
    send_command = threading.Thread(target = send_instructions, args = ())

    # start threads running
    try:
        recieve_data.start()
        time.sleep(1)
        send_command.start()

    except KeyboardInterrupt:
        recieve_data.join()
        send_command.join()