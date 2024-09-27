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
HOST = '127/0.0.1'

# Other constants
PLOT_UPDATE_RATE = 9
TEMP_UPDATE_RATE = 50

# --------------------------------------------------------------------------------------------------------- #

temperature_data = [0]
tf_current_data_received = []
num_peripherals = 0
running = 1
global tf_current_plot
global temperature_plot

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
    global temperature_data_received

    # set up listening sockets
    s_sock = socket(AF_INET, SOCK_DGRAM)
    address = (HOST, ROUTER_PORT4)
    s_sock.bind(address)
    s_sock.settimeout(1)
    print(f'Listening on port:{ROUTER_PORT4}')

    # Call plot function with nothing to create empty plot
    plot(temperature_plot, temperature_data);

    # process data
    while running != 0:
        with contextlib.suppress(timeout):
            msg, _ = s_sock.recvfrom(1024)
            decoded_lsp = struct.unpack('!f', msg)[0]
            temperature_data_received.append(int(decoded_lsp))
            

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

    # update_listbox()

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
    # conn = sqlite3.connect("names.db")
    # c = conn.cursor()

    # c.execute("INSERT INTO names (name) VALUES (?)", (name,))
    # conn.commit()
    # conn.close()

    # update_listbox()

# --------------------------------------------------------------------------------------------------------- #

def linear_interp(waveform):
    waveform_list = waveform.split(',')
    waveform_points_array = np.array(waveform_list, dtype=int)
    x_points = waveform_points_array[:4]
    y_points = waveform_points_array[4:8]
    waveform_interpolated = interp1d(x_points, y_points, kind='linear')
    x_new = np.linspace(0, x_points[3], num=100, endpoint=True)

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

# def update_listbox():
#     conn = sqlite3.connect("names.db")
#     c = conn.cursor()

#     c.execute("SELECT * FROM names")
#     rows = c.fetchall()

#     listbox.delete(0, tk.END)
#     for row in rows:
#         listbox.insert(tk.END, row[1])

#     conn.close()
    
# --------------------------------------------------------------------------------------------------------- #
    
def update_plot(plot_type):
    global tf_current_plot
    global temperature_plot
    global y

    plotted
    update_interval

    # Initialise the plot so that it fills it with the correct data
    if (plot_type == tf_current_plot):
        plotted = tf_current_plot
        y = tf_current_data_received
        update_interval = PLOT_UPDATE_RATE
    elif (plot_type == temperature_plot):
        plotted = temperature_plot
        y = temperature_data
        update_interval = TEMP_UPDATE_RATE

    # if (plot_type == tf_current_data_received):
    #     y = tf_current_data_received
    # elif (plot == temperature_data):
    #     y = temperature_data
    
    # Fill the plot with the cleaned, updated data
    smoothed_y = savgol_filter(y, 7, 2)
    plotted.clear()
    plotted.plot(y, label = 'raw signal', color = 'blue')
    plotted.plot(smoothed_y, label = 'smoothed signal', color = 'red') 
    plotted.figure.canvas.draw_idle()

    # This check is to avoid the interating update_plot() call so it can return to the main receive function
    # and continue to get data, but I may just be interpreting it wrong
    # 
    # if (plot_type == temperature_plot):
    #     temperature_plot.figure.canvas.draw_idle()
    #     return;
    
    app.after(update_interval, update_plot(plot_type))

# --------------------------------------------------------------------------------------------------------- #

def plot(plot_type, data_type):
    global tf_current_plot
    global temperature_plot
    # global y
    fig = Figure(figsize = (8, 5), dpi = 100) 

    plotted
    y
    update_interval

    if (plot_type == tf_current_plot):
        plotted = tf_current_plot
        update_interval = PLOT_UPDATE_RATE
        y = tf_current_data_received
    elif (plot_type == temperature_plot):
        plotted = temperature_plot
        update_interval = TEMP_UPDATE_RATE
        y = temperature_data


    # if (plot_type == tf_current_data_received):
    #     y = tf_current_data_received
    # elif (plot == temperature_data):
    #     y = temperature_data
    
    smoothed_y = savgol_filter(y, 7, 2)
    plotted = fig.add_subplot(111) 
    plotted.plot(y, label = 'raw signal', color = 'blue')
    plotted.plot(smoothed_y, label = 'smoothed signal', color = 'red') 
    plotted.set_xlim(0, len(y))
    plotted.set_ylim(min(y), max(y))
    canvas = FigureCanvasTkAgg(fig, master = app)   
    canvas.draw() 
    canvas.get_tk_widget().pack() 
    toolbar = NavigationToolbar2Tk(canvas, app) 
    toolbar.update() 
    canvas.get_tk_widget().pack()
    
    app.after(update_interval, update_plot(plot_type, data_type))

# --------------------------------------------------------------------------------------------------------- #

# --------------------------------------------------------------------------------------------------------- #

def check_threads():
    global app
    if not tf_current_data_received.is_alive() and not temperature_data.is_alive():
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
app.geometry("1280x720")

# just a simple label
label = tk.Label(app, text="Enter 4 points to outline tf coil current (1st is commands, 2nd is waveform)")
label.pack()

entry = tk.Entry(app)
entry.pack()

tf_entry = tk.Entry(app)
tf_entry.pack()

# list of whatever
# listbox = tk.Listbox(app)
# listbox.pack()
# update_listbox()

# simple button to submit whatever
submit_button = tk.Button(app, text="send command", command = on_submit)
submit_button.pack()

tf_submit_button = tk.Button(app, text="send waveform", command = on_submit_waveform)
tf_submit_button.pack()

# button for graphs
plot_button = tk.Button(app, command = plot, text = "Plot")
plot_button.pack()

# clear_data_button = tk.Button(app, text="Clear data", command = clear)
# clear_data_button.pack()

exit_button = tk.Button(app, text="Exit (gracefully)", command = exit)
exit_button.pack()

selected_value = tk.StringVar()
selected_value.set("TF coil current") 

# trying to implement a dropdown menu thats on pause tho
# dd_menu = ["TF coil current", "Temperature", "etc..."]
# dropdown = tk.OptionMenu(app, selected_value, *options, command=on_select)
# dropdown.pack()

# --------------------------------------------------------------------------------------------------------- #

# create_database()

# --------------------------------------------------------------------------------------------------------- #

if __name__ == "__main__":
    # set up all threads that we want to exist
    tf_current_data_received = threading.Thread(target = receive_from_pynq)
    temperature_data = threading.Thread(target = receive_temp_from_pynq)

    # start threads running
    tf_current_data_received.start()
    temperature_data.start()
    
    # start app window
    app.mainloop()


        