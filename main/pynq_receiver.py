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

# Receive current control address
ROUTER_PORT3 = 1400

# Send temperature address
ROUTER_PORT_TEMPERATURE = 1500

# Send pressure address
ROUTER_PORT_PRESSURE = 1600

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

# Function that creates a receiving socket and listens for commmands
# It sends the command to the hand_command fucntio which the executes the correct function
# according to the command.
#
def receive_commands():
    global data_received

    # set up listening sockets
    s_sock = socket(AF_INET, SOCK_DGRAM)
    address = (HOST, ROUTER_PORT2)
    s_sock.bind(address)
    print(f'Listening on port:{ROUTER_PORT2}')

    # proccess data this is not right just very placeholder
    while running:
        msg, _ = s_sock.recvfrom(1024)
        decoded_lsp = msg.decode()
        # print(f"\n+received {decoded_lsp}")
        handle_command(decoded_lsp)

# --------------------------------------------------------------------------------------------------------- #

# This is the receiver for the waveform data. It creates the receiving socket and listens for the waveform
# data. It then sends it to the drive_tf_current function which will map the data and send it to the PC.
#
def receive_waveform():
    global data_received
    global next_waveform
    
    # set up listening sockets
    s_sock = socket(AF_INET, SOCK_DGRAM)
    address = (HOST, ROUTER_PORT3)
    s_sock.bind(address)

    # process data
    while running:
        msg, _ = s_sock.recvfrom(1024)
        decoded_lsp = msg.decode()
        ref_current_map = decoded_lsp.split()
        drive_tf_current(ref_current_map)

# --------------------------------------------------------------------------------------------------------- #

# Function that maps the received data to the pmod port values. 
# 
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

# This is where the PYNQ code will go using the mapped waveform, for now we will just send it back to the PC
# as a test.
# What we do here is some mapping and that to of the received linearly interpolated data and drive that
# through the pmod port to the current control system. just placeholder for now.
#
def drive_tf_current(reference_current):
    global mapped_waveform
    mapped_waveform = map_pynq_pmod(reference_current)
    send_data()
        
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


# This is code for the pynq probably that is sending packets, however can be used here to send
# information for control actually (may or may not work). Again just copied my own old code
# will need restructuring to do what we want it to.
#
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

def send_temperatures_test():
    # THIS FUNCTION IS A TEST FUNCTION TO SEND TEMPERATURES TO THE PC
    # TO BE REMOVED AT A LATER DATE
    while True:
        c_sock = socket(AF_INET, SOCK_DGRAM)
        send_address = (HOST, ROUTER_PORT_TEMPERATURE)
        data_sent = str(random.randint(50, 100))
        packet = data_sent.encode()
        c_sock.sendto(packet, send_address)
        time.sleep(0.5)
        
def placeholder_temperature_starter():
    # send_test_temperatures = threading.Thread(target = send_temperatures_test)
    send_test_temperatures.start()
    
# --------------------------------------------------------------------------------------------------------- #

    
def send_pressure_test():
    # THIS FUNCTION IS A TEST FUNCTION TO SEND PRESSURES TO THE PC
    # TO BE REMOVED AT A LATER DATE
    while True:
        c_sock = socket(AF_INET, SOCK_DGRAM)
        send_address = (HOST, ROUTER_PORT_PRESSURE)
        # data_sent = str(random.randint(50, 100))
        data_sent = "{:.2f}".format(random.uniform(50, 100))
        packet = data_sent.encode()
        c_sock.sendto(packet, send_address)
        time.sleep(0.5)
        
def placeholder_pressure_starter():
    # send_test_pressure = threading.Thread(target = send_pressure_test)
    send_test_pressure.start()

# --------------------------------------------------------------------------------------------------------- #

# def start_send_thread():
#     start_send_data = threading.Thread(target = send_data)
#     # start_tf_drive = threading.Thread(target = drive_tf_current)
#     start_send_data.start()
#     # start_tf_drive.start()

# --------------------------------------------------------------------------------------------------------- #

# List of commands that can be interpreted by the pynq. It is different to the PC commands
# since the pynq will be handling different things.
#
commands = {
    # "start control loop": start_send_thread,
    "temperature test": placeholder_temperature_starter,
    "pressure test": placeholder_pressure_starter
}

def handle_command(command):
    if command in commands:
        commands[command]()
    else:
        print("Unknown command")


# --------------------------------------------------------------------------------------------------------- #

# Main function that starts the threads and runs the program.
#
if __name__ == "__main__":

    # set up all threads that we want to exist
    receive_command = threading.Thread(target = receive_commands)
    receive_wave = threading.Thread(target = receive_waveform)
    start_send_data = threading.Thread(target = send_data)
    send_test_temperatures = threading.Thread(target = send_temperatures_test)
    send_test_pressure = threading.Thread(target = send_pressure_test)

    # start threads running
    try:
        receive_command.start()
        receive_wave.start()

    except KeyboardInterrupt:
        receive_command.join()