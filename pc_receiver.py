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
ROUTER_PORT = 1200
HOST = '127.0.0.1'

# Send address
ROUTER_PORT2 = 1200
HOST2 = '192.168.2.99'

# --------------------------------------------------------------------------------------------------------- #

data_received = {}
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
        # print(decoded_lsp)

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
def send_instructions():
    c_sock = socket(AF_INET, SOCK_DGRAM)

    # should just send a packet with a random number that I type into command line
    while(True):
        input_command = input("Send a number to the pynq")
        print("sending",input_command)
        packet = input_command.encode()
        send_address = (HOST, ROUTER_PORT)
        c_sock.sendto(packet, send_address)

    # while(True):
    #     temp_table = routing_table
    #     for x in range(num_neighs):
    #         port_access = neighbours[x]
    #         temp_port = int(port_access[len(port_access) - 4:])

    #         for x in range(len(temp_table)):
    #             packet = temp_table[x].encode()

    #             send_address = (HOST, temp_port)
    #             c_sock.sendto(packet, send_address)

# --------------------------------------------------------------------------------------------------------- #

if __name__ == "__main__":

    # set up all threads that we want to exist
    recieve_data = threading.Thread(target=receive_from_pynq)
    send_command = threading.Thread(target = send_instructions, args = ())

    # send_thread = threading.Thread(target = send_neighbours, args = ())
    # compute_djisktras = threading.Thread(target = Djisktras_routing, args = (ROUTER_ID))
    # send_hb_thread = threading.Thread(target = send_heartbeat, args = ())
    # check_hb_thread = threading.Thread(target = monitor_router_activity, args = ())

    # start threads running
    try:
        recieve_data.start()
        send_command.start()

    except KeyboardInterrupt:
        recieve_data.join()
        send_command.join()