# plan here is to write python code that will receive the sockets sent from the pynq and then.
# if that is able to receive quickly then we can use that in the controller.py file to actually
# create a nice bit of software.

import contextlib
from socket import *
import struct
import threading
import time
from collections import defaultdict
import tkinter as tk
import sqlite3
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
from scipy.signal import savgol_filter 
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

# Receive TF Coil Current address
ROUTER_PORT = 1300
HOST = '127.0.0.1'

# Send address
ROUTER_PORT2 = 1200
HOST2 = '127.0.0.1'

# Send current control address
ROUTER_PORT3 = 1400
HOST2 = '127.0.0.1'

# Receive Temp address
ROUTER_PORT4 = 1500
HOST = '127.0.0.1'

# Receive Temp address
ROUTER_PORT5 = 1600
HOST = '127.0.0.1'

# Other constants
DEFAULT_UPDATE_RATE = 100

# --------------------------------------------------------------------------------------------------------- #

temperature_data = [25] * 100
tf_current_data_received = [10] * 100
y_alpha = [0] * 100
y_beta = [0] * 100
num_peripherals = 0
running = 1
global tf_current_plot
global temperature_plot
update_lock = threading.Lock()

# --------------------------------------------------------------------------------------------------------- #

# Receiving TF Coil Current data from the pynq. It creates the listening socket, then processes
# the data it receives constantly until the program ends, or it receives no more data
def receive_from_pynq():
    global tf_current_data_received
    global running

    # set up listening sockets
    s_sock = socket(AF_INET, SOCK_DGRAM)
    address = (HOST2, ROUTER_PORT2)
    s_sock.bind(address)
    s_sock.settimeout(1)
    print(f'Listening on port:{ROUTER_PORT2}')

    # process data this is not right just very placeholder
    while running != 0:
        with contextlib.suppress(timeout):
            msg, _ = s_sock.recvfrom(1024)
            # decoded_lsp = msg.decode()
            decoded_lsp = struct.unpack('!f', msg)[0]

            # print(f"\n+received {decoded_lsp}")
            tf_current_data_received.append(int(decoded_lsp))

# --------------------------------------------------------------------------------------------------------- #

# Similar function to receive_from_pynq, except it will gather the temperature data from the pynq,
# then process it in the same way. The graphing will happen incrementally, every 0.5 seconds or so to save memory
def receive_temp_from_pynq():
    global temperature_data
    global temperature_plot

    # set up listening sockets
    s_sock = socket(AF_INET, SOCK_DGRAM)
    address = (HOST, ROUTER_PORT4)
    s_sock.bind(address)
    s_sock.settimeout(1)
    print(f'Listening on port:{ROUTER_PORT4}')

    # process data
    while running != 0:
        with contextlib.suppress(timeout):
            msg, _ = s_sock.recvfrom(1024)
            decoded_lsp = msg.decode()
            # decoded_lsp = struct.unpack('!f', msg)[0]
            temperature_data.append(int(decoded_lsp))
            

# --------------------------------------------------------------------------------------------------------- #

# this is code for the pynq probably that is sending packets, however can be used here to send
# information for control.
def send_instructions(command):
    if isinstance(command, list):
        command = ' '.join(command)
    c_sock = socket(AF_INET, SOCK_DGRAM)
    # print("-sending",command)
    packet = command.encode()
    send_address = (HOST, ROUTER_PORT)
    c_sock.sendto(packet, send_address)

# --------------------------------------------------------------------------------------------------------- #

def send_waveform(command):
    if isinstance(command, list):
        command = ' '.join(command)
    c_sock = socket(AF_INET, SOCK_DGRAM)
    # print("-sending",command)
    packet = command.encode()
    send_address = (HOST, ROUTER_PORT3)
    c_sock.sendto(packet, send_address)

# --------------------------------------------------------------------------------------------------------- #

def clear():
    conn = sqlite3.connect("names.db")
    c = conn.cursor()

    c.execute("DELETE FROM names")

    conn.commit()
    conn.close()

# --------------------------------------------------------------------------------------------------------- #

def create_database():
    conn = sqlite3.connect("names.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS names (id INTEGER PRIMARY KEY,name TEXT)""")
    conn.commit()
    conn.close()

# ---------------,------------------------------------------------------------------------------------------ #

def on_submit():
    command = entry.get()
    send_instructions(command)

# --------------------------------------------------------------------------------------------------------- #

def linear_interp(waveform):
    waveform_list = waveform.split(',')
    waveform_points_array = np.array(waveform_list, dtype=int)
    x_points = waveform_points_array[:4]
    y_points = waveform_points_array[4:8]
    waveform_interpolated = interp1d(x_points, y_points, kind='linear')
    x_new = np.linspace(1, x_points[3], num=100, endpoint=True)

    interpolated_points = waveform_interpolated(x_new)
    
    interp_list = interpolated_points.tolist()
    return list(map(str, interp_list))

# --------------------------------------------------------------------------------------------------------- #


def on_submit_waveform():
    waveform = tf_entry.get()
    interpolated = linear_interp(waveform)
    send_waveform(interpolated)

    # if we really want to we can plot the ref current but its not necessary until after we receive the measured
    # current back from the pynq
    
    # plt.plot(x_new, interpolated_points, '-', label='Reference Current')
    # plt.xlabel('x')
    # plt.ylabel('y')
    # plt.title('Reference Current')
    # plt.legend()
    # plt.show()
    
# --------------------------------------------------------------------------------------------------------- #
    
# hopefully this function is cohesive enough that it works for plot alpha and beta
def update_plot(plotted, parent_plot):
    update_lock.acquire()
    try:
        if isinstance(y_alpha, (list, np.ndarray)) and parent_plot == "alpha":
            # Fill the plot with the cleaned, updated data
            smoothed_y = savgol_filter(y_alpha, 7, 2)
            plotted.clear()
            plotted.plot(y_alpha, label = 'raw signal', color = 'blue')
            plotted.plot(smoothed_y, label = 'smoothed signal', color = 'red') 
            plotted.figure.canvas.draw_idle()
        elif isinstance(y_beta, (list, np.ndarray)) and parent_plot == "beta":
            # Fill the plot with the cleaned, updated data
            smoothed_y = savgol_filter(y_beta, 7, 2)
            plotted.clear()
            plotted.plot(y_beta, label = 'raw signal', color = 'blue')
            plotted.plot(smoothed_y, label = 'smoothed signal', color = 'red') 
            plotted.figure.canvas.draw_idle()
            
        else:
            print("Invalid data type")
    finally:
        update_lock.release()
    
    app.after(DEFAULT_UPDATE_RATE, lambda: update_plot(plotted, parent_plot))

# --------------------------------------------------------------------------------------------------------- #

# rename to plot_alpha. need to extend functionality to be interchangeable graphs with different data
def plot_alpha():    
    fig = Figure(figsize = (5, 2), dpi = 100)
    plotted = fig.add_subplot(111) 
    
    smoothed_y = savgol_filter(y_alpha, 7, 2)    
    plotted = fig.add_subplot(111) 
    plotted.plot(y_alpha, label = 'raw signal', color = 'blue')
    plotted.plot(smoothed_y, label = 'smoothed signal', color = 'red') 
    plotted.set_xlim(0, len(y_alpha))
    # placeholder min max values until we can confirm our currents
    plotted.set_ylim(0, 100)
    canvas = FigureCanvasTkAgg(fig, master = app)   
    canvas.draw() 
    canvas.get_tk_widget().pack() 
    toolbar = NavigationToolbar2Tk(canvas, app) 
    toolbar.update() 
    canvas.get_tk_widget().pack()
    
    app.after(DEFAULT_UPDATE_RATE, lambda: update_plot(plotted, "alpha"))
    
def plot_beta():    
    fig = Figure(figsize = (5, 2), dpi = 100)
    plotted = fig.add_subplot(111) 
    
    smoothed_y = savgol_filter(y_beta, 7, 2)    
    plotted = fig.add_subplot(111) 
    plotted.plot(y_beta, label = 'raw signal', color = 'blue')
    plotted.plot(smoothed_y, label = 'smoothed signal', color = 'red') 
    plotted.set_xlim(0, len(y_alpha))
    # placeholder min max values until we can confirm our currents
    plotted.set_ylim(0, 100)
    canvas = FigureCanvasTkAgg(fig, master = app)   
    canvas.draw() 
    canvas.get_tk_widget().pack() 
    toolbar = NavigationToolbar2Tk(canvas, app) 
    toolbar.update() 
    canvas.get_tk_widget().pack()
    
    app.after(DEFAULT_UPDATE_RATE, lambda: update_plot(plotted, "beta"))

# --------------------------------------------------------------------------------------------------------- #

def switch_plot_alpha():
    global y_alpha
    data_to_plot = alpha_plot_data.get()
    if (data_to_plot == "Current"):
        y_alpha = tf_current_data_received
    elif (data_to_plot == "Temperature"):
        y_alpha = temperature_data
    
def switch_plot_beta():
    global y_beta
    data_to_plot = beta_plot_data.get()
    if (data_to_plot == "Current"):
        y_beta = tf_current_data_received
    elif (data_to_plot == "Temperature"):
        y_beta = temperature_data

# --------------------------------------------------------------------------------------------------------- #

def receive_pressure():
    # set up listening sockets
    s_sock = socket(AF_INET, SOCK_DGRAM)
    address = (HOST, ROUTER_PORT5)
    s_sock.bind(address)
    s_sock.settimeout(1)
    print(f'Listening on port:{ROUTER_PORT5}')

    # process data
    while running != 0:
        with contextlib.suppress(timeout):
            msg, _ = s_sock.recvfrom(1024)
            decoded_lsp = msg.decode()
            number_label.config(text=decoded_lsp)

# --------------------------------------------------------------------------------------------------------- #

def check_threads():
    global app
    if not tf_current_data_thread.is_alive() and not temperature_data_thread.is_alive():
        app.destroy()
    else:app.after(100, check_threads)
    
# --------------------------------------------------------------------------------------------------------- #

def exit():
    global running
    running = 0
    check_threads()


# --------------------------------------------------------------------------------------------------------- #

# programs title
app = tk.Tk()
app.title("AtomCraft Controller")
app.geometry("1920x1080")

# just a simple label
label = tk.Label(app, text="Enter 4 points to outline tf coil current (1st is commands, 2nd is waveform)")
label.pack()

entry = tk.Entry(app)
entry.pack()

tf_entry = tk.Entry(app)
tf_entry.pack()

# simple button to submit whatever
submit_button = tk.Button(app, text="send command", command = on_submit)
submit_button.pack()

tf_submit_button = tk.Button(app, text="send waveform", command = on_submit_waveform)
tf_submit_button.pack()

number_label = tk.Label(app, text="0.00", font=("Helvetica", 48))
number_label.pack(pady=20)

# --------------------------------------------------------------------------------------------------------- #

alpha_dd_menu = ["Current", "Temperature"]

# dd for plot_alpha
alpha_plot_data = tk.StringVar()
alpha_plot_data.set("Select Variable To Plot") 
alpha_plot_data.trace_add("write", lambda *args: switch_plot_alpha())

alpha_dropdown = tk.OptionMenu(app, alpha_plot_data, *alpha_dd_menu)
alpha_dropdown.pack()
# alpha_dd_button = tk.Button(app, text= "Select Plot", command = on_submit_plot)
# alpha_dd_button.pack()

plot_alpha()

# --------------------------------------------------------------------------------------------------------- #

beta_dd_menu = ["Current", "Temperature"]

# dd for plot_alpha
beta_plot_data = tk.StringVar()
beta_plot_data.set("Select Variable To Plot") 
beta_plot_data.trace_add("write", lambda *args: switch_plot_beta())

beta_dropdown = tk.OptionMenu(app, beta_plot_data, *beta_dd_menu)
beta_dropdown.pack()
# alpha_dd_button = tk.Button(app, text= "Select Plot", command = on_submit_plot)
# alpha_dd_button.pack()

plot_beta()

# --------------------------------------------------------------------------------------------------------- #

exit_button = tk.Button(app, text="Exit (gracefully)", command = exit)
exit_button.pack()

# --------------------------------------------------------------------------------------------------------- #

if __name__ == "__main__":
    # set up all threads that we want to exist
    tf_current_data_thread = threading.Thread(target = receive_from_pynq)
    temperature_data_thread = threading.Thread(target = receive_temp_from_pynq)
    pressure_data_thread = threading.Thread(target = receive_pressure)


    # start threads running
    tf_current_data_thread.start()
    temperature_data_thread.start()
    pressure_data_thread.start()
    
    # start app window
    app.mainloop()


        