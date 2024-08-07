# plan here is to write python code that will receive the sockets sent from the pynq and then.
# if that is able to receive quickly then we can use that in the controller.py file to actually
# create a nice bit of software.

import struct
import sys
from socket import *
import threading
import time
from collections import defaultdict
import heapq
import random
import matplotlib.pyplot as plt


# Send address
ROUTER_PORT = 1200
HOST = '127.0.0.1'

# Receive commands address
ROUTER_PORT2 = 1300
HOST2 = '127.0.0.1'

# Receive current control address
ROUTER_PORT3 = 1400
HOST2 = '127.0.0.1'

# CONSTANTS
TIMESCALE = 3000 # in miliseconds
NUMBER_OF_POINTS = 100 

# --------------------------------------------------------------------------------------------------------- #

data_received = []
num_peripherals = 0
running = 1
next_waveform = []
mapped_waveform = []

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
        msg, _ = s_sock.recvfrom(1024)
        decoded_lsp = msg.decode()
        # print(f"\n+received {decoded_lsp}")
        handle_command(decoded_lsp)

# --------------------------------------------------------------------------------------------------------- #

def receive_waveform():
    global data_received
    global next_waveform
    
    # set up listening sockets
    s_sock = socket(AF_INET, SOCK_DGRAM)
    address = (HOST2, ROUTER_PORT3)
    s_sock.bind(address)

    # process data
    while running:
        msg, _ = s_sock.recvfrom(1024)
        decoded_lsp = msg.decode()
        ref_current_map = decoded_lsp.split()
        drive_tf_current(ref_current_map)
        # next_waveform = (list(float, ref_current_map))

    # put the list of current values into data_received


    # idk why you're listening for command i'll just comment for now
    # handle_command(command_list)

# --------------------------------------------------------------------------------------------------------- #

def map_pynq_pmod(reference_current):
    # Convert all elements to float
    reference_current = [float(x) for x in reference_current]

    min_value = 1
    max_value = 99
    min_x = min(reference_current)
    max_x = max(reference_current)

    return (
        [min_value] * len(reference_current)
        if min_x == max_x
        else [
            min_value + (max_value - min_value) * (x - min_x) / (max_x - min_x)
            for x in reference_current
        ]
    )

# --------------------------------------------------------------------------------------------------------- #

def drive_tf_current(reference_current):
    global mapped_waveform
    # what we do here is some mapping and that to of the received linearly interpolated data and drive that
    # through the pmod port to the current control system. just placeholder for now.
    mapped_waveform = map_pynq_pmod(reference_current)
    
    # This is where the PYNQ code will go using the mapped waveform, for now we will just send it back to the PC
    # print("Mapped waveform:", mapped_waveform)
        
# --------------------------------------------------------------------------------------------------------- #

# function that takes current_time (from time zero right so will need to be
# externally subtract start time) and gives the matching     
def map_float_to_value(current_time):
    # no bounds check cause speed please enter right values
    
    # Normalize and find the corresponding index
    index = int(current_time / TIMESCALE * NUMBER_OF_POINTS)
    
    # Handle the edge case where 
    if index == TIMESCALE:
        index = TIMESCALE - 1

    # Return the value from the list
    return data_received[index]

# --------------------------------------------------------------------------------------------------------- #


# this is code for the pynq probably that is sending packets, however can be used here to send
# information for control actually (may or may not work). Again just copied my own old code
# will need restructuring to do what we want it to.
def send_data():
    global mapped_waveform
    c_sock = socket(AF_INET, SOCK_DGRAM)
    # run_time = time.time() + 3
    send_address = (HOST, ROUTER_PORT)

    for waveform_value in mapped_waveform:
        time.sleep(0.01)
        # packet = str_waveform_value.encode()
        packet = struct.pack('!f', waveform_value)
        c_sock.sendto(packet, send_address)
        # time.sleep(0.1)


    # should just send a packet with a random number that I type into command line
    # while time.time() < run_time:
    #     data_sent = str(random.randint(10, 20))
    #     time.sleep(0.01)
    #     print("sending",data_sent)
    #     packet = data_sent.encode()
    #     send_address = (HOST, ROUTER_PORT)
    #     c_sock.sendto(packet, send_address)
    #     time.sleep(0.1)

# --------------------------------------------------------------------------------------------------------- #

def start_send_thread():
    start_send_data = threading.Thread(target = send_data)
    # start_tf_drive = threading.Thread(target = drive_tf_current)
    start_send_data.start()
    # start_tf_drive.start()

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
    receive_wave = threading.Thread(target = receive_waveform)
    start_send_data = threading.Thread(target = send_data)

    # start threads running
    try:
        receive_command.start()
        receive_wave.start()

    except KeyboardInterrupt:
        receive_command.join()