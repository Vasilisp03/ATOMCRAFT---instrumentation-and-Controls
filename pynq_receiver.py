# plan here is to write python code that will recieve the sockets sent from the pynq and then.
# if that is able to recieve quickly then we can use that in the controller.py file to actually
# create a nice bit of software.

import sys
from socket import *
import threading
import time
from collections import defaultdict
import heapq
import random

# Send address
ROUTER_PORT = 1200
HOST = '127.0.0.1'

# Receive address
ROUTER_PORT2 = 1300
HOST2 = '127.0.0.1'

# --------------------------------------------------------------------------------------------------------- #

data_received = []
num_peripherals = 0

# --------------------------------------------------------------------------------------------------------- #

def receive_commands():
    global data_received

    # set up listening sockets
    s_sock = socket(AF_INET, SOCK_DGRAM)
    address = (HOST2, ROUTER_PORT2)
    s_sock.bind(address)
    print(f'Listening on port:{ROUTER_PORT2}')

    # proccess data this is not right just very placeholder
    while True:
        msg, c_add = s_sock.recvfrom(1024)
        decoded_lsp = msg.decode()
        print(f"\n+received {decoded_lsp}")

        data_received.append(decoded_lsp)

        # if decoded_lsp[:9] == 'Heartbeat':
        #     if network:
        #         network[decoded_lsp[-1]]['last_heard'] = time.time()
        # elif decoded_lsp not in routing_table:
        #     routing_table.append(decoded_lsp)

# --------------------------------------------------------------------------------------------------------- #

# this is code for the pynq probably that is sending packets, however can be used here to send
# information for control actually (may or may not work). Again just copied my own old code
# will need restructuring to do what we want it to.
def send_data():
    c_sock = socket(AF_INET, SOCK_DGRAM)

    # should just send a packet with a random number that I type into command line
    # while(True):
    #     data_sent = str(random.randint(10, 20))
    #     print("sending",data_sent)
    #     packet = data_sent.encode()
    #     send_address = (HOST, ROUTER_PORT)
    #     c_sock.sendto(packet, send_address)
    #     time.sleep(0.1)


    # just for testing sending and receiving a packet to and from pynq
    while(True):
        input_command = input("Send a number to the pc: ")
        print("-sending",input_command)
        packet = input_command.encode()
        send_address = (HOST, ROUTER_PORT)
        c_sock.sendto(packet, send_address)

# --------------------------------------------------------------------------------------------------------- #

if __name__ == "__main__":

    # set up all threads that we want to exist
    recieve_command = threading.Thread(target=receive_commands)
    send_data = threading.Thread(target = send_data, args = ())

    # send_thread = threading.Thread(target = send_neighbours, args = ())
    # compute_djisktras = threading.Thread(target = Djisktras_routing, args = (ROUTER_ID))
    # send_hb_thread = threading.Thread(target = send_heartbeat, args = ())
    # check_hb_thread = threading.Thread(target = monitor_router_activity, args = ())

    # start threads running
    try:
        recieve_command.start()
        time.sleep(1)
        send_data.start()

    except KeyboardInterrupt:
        recieve_command.join()
        send_data.join()