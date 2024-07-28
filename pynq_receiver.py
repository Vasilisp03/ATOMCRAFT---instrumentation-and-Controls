# plan here is to write python code that will receive the sockets sent from the pynq and then.
# if that is able to receive quickly then we can use that in the controller.py file to actually
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

# Receive commands address
ROUTER_PORT2 = 1300
HOST2 = '127.0.0.1'

# Receive current control address
ROUTER_PORT3 = 1400
HOST2 = '127.0.0.1'

# --------------------------------------------------------------------------------------------------------- #

data_received = []
num_peripherals = 0
running = 1

# --------------------------------------------------------------------------------------------------------- #

def receive_commands():
    global data_received

    # set up listening sockets
    s_sock = socket(AF_INET, SOCK_DGRAM)
    address = (HOST2, ROUTER_PORT2)
    s_sock.bind(address)
    print(f'Listening on port:{ROUTER_PORT2}')

    # proccess data this is not right just very placeholder
    while running:
        msg, c_add = s_sock.recvfrom(1024)
        decoded_lsp = msg.decode()
        # print(f"\n+received {decoded_lsp}")
        handle_command(decoded_lsp)

# --------------------------------------------------------------------------------------------------------- #

def receive_waveform():

    # set up listening sockets
    s_sock = socket(AF_INET, SOCK_DGRAM)
    address = (HOST2, ROUTER_PORT3)
    s_sock.bind(address)

    # process data
    msg, c_add = s_sock.recvfrom(1024)
    decoded_lsp = msg.decode()
    command_list = decoded_lsp.split()
    # print(f"\n+received {command_list}")
    handle_command(command_list)

# --------------------------------------------------------------------------------------------------------- #

def start_tf_drive():
    # what we do here is some mapping and that to of the received linearly interpolated data and drive that
    # through the pmod port to the current control system. just placeholder for now.
    pass

# --------------------------------------------------------------------------------------------------------- #


# this is code for the pynq probably that is sending packets, however can be used here to send
# information for control actually (may or may not work). Again just copied my own old code
# will need restructuring to do what we want it to.
def send_data():
    c_sock = socket(AF_INET, SOCK_DGRAM)
    run_time = time.time() + 5

    # should just send a packet with a random number that I type into command line
    while time.time() < run_time:
        data_sent = str(random.randint(10, 20))
        time.sleep(0.01)
        # print("sending",data_sent)
        packet = data_sent.encode()
        send_address = (HOST, ROUTER_PORT)
        c_sock.sendto(packet, send_address)
        time.sleep(0.1)

# --------------------------------------------------------------------------------------------------------- #

def start_send_thread():
    start_send_data = threading.Thread(target = send_data)
    start_tf_drive = threading.Thread(target = drive_tf_current)
    start_send_data.start()
    start_tf_drive.start()

# --------------------------------------------------------------------------------------------------------- #

commands = {
    "start control loop": start_send_thread,
}

def handle_command(command):
    if command in commands:
        commands[command]()
    else:
        print("Unknown command")


# --------------------------------------------------------------------------------------------------------- #

if __name__ == "__main__":

    # set up all threads that we want to exist
    receive_command = threading.Thread(target = receive_commands)
    start_send_data = threading.Thread(target = send_data)

    # start threads running
    try:
        receive_command.start()

    except KeyboardInterrupt:
        receive_command.join()