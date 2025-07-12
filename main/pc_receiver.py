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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
import numpy as np
from scipy.signal import savgol_filter 
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import re

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
global waiting_for_waveform
waiting_for_waveform = False
global tf_current_plot
global temperature_plot
update_lock = threading.Lock()

# --------------------------------------------------------------------------------------------------------- #

# Receiving TF Coil Current data from the pynq. It creates the listening socket, then processes
# the data it receives constantly until the program ends, or it receives no more data
#
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
#
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
#
def send_instructions(command):
    if isinstance(command, list):
        command = ' '.join(command)
    c_sock = socket(AF_INET, SOCK_DGRAM)
    # print("-sending",command)
    packet = command.encode()
    send_address = (HOST, ROUTER_PORT)
    c_sock.sendto(packet, send_address)

# --------------------------------------------------------------------------------------------------------- #

# This code is similar to sen_instruction, however it is used to send the waveform to the pynq
# It does so by setting the socket, then packing the waveform into a packet, then sending it
#
def send_waveform(command):
    if isinstance(command, list):
        command = ' '.join(command)
    c_sock = socket(AF_INET, SOCK_DGRAM)
    packet = command.encode()
    send_address = (HOST, ROUTER_PORT3)
    c_sock.sendto(packet, send_address)

# --------------------------------------------------------------------------------------------------------- #

# Clear empties out the database, removing all items from the listbox
#
def clear():
    conn = sqlite3.connect("data/names.db")
    c = conn.cursor()

    c.execute("DELETE FROM names")

    conn.commit()
    conn.close()

# --------------------------------------------------------------------------------------------------------- #

# Creates the database for the listbox, then creates the table for the names
#
def create_database():
    conn = sqlite3.connect("data/names.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS names (id INTEGER PRIMARY KEY,name TEXT)""")
    conn.commit()
    conn.close()

# ---------------------------------------------------------------------------------------------------------- #

# When the user types and hits enter for a command, this function is called.
# It will recieve the command, add it to the database, then do checks
#
# If the previous command was to start the control loop for current, it will await the correct format,
# (i.e. 1, 2, 3, 4, 1, 10, 10, 1) to send. If the command doesn't fit this format, it will return and await another input
# that fits the format.
#
# If the command is 'cancel control', it will reset waiting_for_waveform to False, then return, allowing the user to input
# an alternative command.
#
def on_submit(event = None):
    global waiting_for_waveform
    command = entry.get()
    add_to_db(command)
    if (waiting_for_waveform):  
        if (command == 'cancel control'):
            waiting_for_waveform = False
            add_to_db("Exiting control loop")
            entry.delete(0, tk.END)
            return
               
        verify_waveform(command)

    else:
        handle_command(command)
        send_instructions(command)
    
    # Clear the entry box
    entry.delete(0, tk.END)

# --------------------------------------------------------------------------------------------------------- #

# This function is called when the user inputs a waveform after 'start control loop'.
#
# If the input is valid, then send the waveform through on_submit_waveform. 
#
# Else, it will add an error message to the database, then return to await another input.
#
def verify_waveform(waveform):
    global waiting_for_waveform
    input_waveform = waveform.split(',')

    if (len(input_waveform) == 8 and all(bool(re.search(r'\d', i)) for i in input_waveform)):
        input_waveform_ints = np.array(input_waveform, dtype=int)
        waiting_for_waveform = False
        on_submit_waveform(input_waveform_ints)
    
    else:
        add_to_db("Invalid waveform input")

# --------------------------------------------------------------------------------------------------------- #

# This function adds what the most recent command was to the database, then updates the listbox by calling
# update_listbox
#
def add_to_db(name):
    conn = sqlite3.connect("data/names.db")
    c = conn.cursor()

    c.execute("INSERT INTO names (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

    update_listbox()

# --------------------------------------------------------------------------------------------------------- #

# This function updates the listbox with the most recent commands
# If the listbox is full, it will scroll to the bottom to show the most recent commands
#
def update_listbox():
    conn = sqlite3.connect("data/names.db")
    c = conn.cursor()

    c.execute("SELECT * FROM names")
    rows = c.fetchall()

    listbox.delete(0, tk.END)
    for row in rows:
        listbox.insert(tk.END, row[1])
    
    if rows:
        listbox.see(tk.END)

    conn.close()

# --------------------------------------------------------------------------------------------------------- #

# This function takes the waveform input, then interpolates the points to create a smooth waveform.
# This is the red line that overlaps the raw data in the graph.
#
def linear_interp(waveform):
    # waveform_list = waveform.split(',')
    # waveform_points_array = np.array(waveform_list, dtype=int)
    x_points = waveform[:4]
    y_points = waveform[4:8]
    waveform_interpolated = interp1d(x_points, y_points, kind='linear')
    x_new = np.linspace(1, x_points[3], num=100, endpoint=True)

    interpolated_points = waveform_interpolated(x_new)
    
    interp_list = interpolated_points.tolist()
    return list(map(str, interp_list))

# --------------------------------------------------------------------------------------------------------- #

# This function takes in the raw waveform, then interpolates it to create a smooth waveform.
# Then it send it to the pynq to control the current.
#
def on_submit_waveform(waveform):
    # waveform = entry.get()
    interpolated = linear_interp(waveform)
    send_waveform(interpolated)

# This function is called when the user inputs a waveform after 'start control loop'.
# It sets waiting_for_waveform to True, making on_submit aware that it is waiting for a waveform.
#
def prompt_for_waveform():
    global waiting_for_waveform
    waiting_for_waveform = True

    add_to_db("Input time scale and key points")
    add_to_db("(E.g. 1, 2, 3, 4, 1, 10, 10, 1):")

    
# --------------------------------------------------------------------------------------------------------- #
    
# hopefully this function is cohesive enough that it works for plot alpha and beta
# This function is called every 0.1 seconds to update the plot with the most recent data
# It will lock the update_lock, then check if the data is valid and for which plot it is for.
#
# If the data is valid, it will clear the plot, then plot the raw data and the smoothed data.
# The lock is then released, allowing another thread to access the data.
# This was done so that the data is not accessed by multiple threads at once, causing
# the plots to be incorrect.
#
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

# This is the main function for one of the plots. It creates the plot, sets the colours, and then awaits data
# to plot. It will plot the raw data and the smoothed data. This plot interacts with the alpha_plot_data dropdown menu
# which allows the user to switch between plotting the current and the temperature.
#
def plot_alpha():    
    fig = Figure(figsize = (4, 3), dpi = 100)
    fig.set_facecolor('#1D1D1D')

    plotted = fig.add_subplot(111)
    # plotted.set_facecolor('black')
    
    smoothed_y = savgol_filter(y_alpha, 7, 2)    
    plotted = fig.add_subplot(111) 
    plotted.plot(y_alpha, label = 'raw signal', color = 'blue')
    plotted.plot(smoothed_y, label = 'smoothed signal', color = 'red') 
    plotted.set_xlim(0, len(y_alpha))
    # placeholder min max values until we can confirm our currents
    plotted.set_ylim(0, 100)

    # Set the color of the axis labels and ticks
    plotted.spines['bottom'].set_color('#C65D3B')
    plotted.spines['top'].set_color('#C65D3B')
    plotted.spines['right'].set_color('#C65D3B')
    plotted.spines['left'].set_color('#C65D3B')
    plotted.xaxis.label.set_color('#C65D3B')
    plotted.yaxis.label.set_color('#C65D3B')
    plotted.tick_params(axis='x', colors='white')
    plotted.tick_params(axis='y', colors='white')

    canvas = FigureCanvasTkAgg(fig, master = app)   
    canvas.draw() 
    canvas.get_tk_widget().place(relx=0.3, rely=0.14) 
    toolbar = NavigationToolbar2Tk(canvas, app) 
    toolbar.update() 
    canvas.get_tk_widget().place(relx=0.3, rely=0.14) 
    
    app.after(DEFAULT_UPDATE_RATE, lambda: update_plot(plotted, "alpha"))
    
# This plot is the same as plot_alpha, except it is for the beta plot.
# The reason it is done separately is so that the user can switch between the two plots and 
# the data is not mixed up. It is also because having multiple plot functions will allow easier 
# debugging and readability.
#
# The downside is that there is a lot of repeated code, which could be refactored into a single function
# that takes in the data to plot and the plot to plot it on. This has it's own issues, so for now, this
# is the best solution.
#
def plot_beta():    
    fig = Figure(figsize = (4, 3), dpi = 100)
    fig.set_facecolor('#1D1D1D')

    plotted = fig.add_subplot(111) 
    
    smoothed_y = savgol_filter(y_beta, 7, 2)    
    plotted = fig.add_subplot(111) 
    plotted.plot(y_beta, label = 'raw signal', color = 'blue')
    plotted.plot(smoothed_y, label = 'smoothed signal', color = 'red') 
    plotted.set_xlim(0, len(y_alpha))
    # placeholder min max values until we can confirm our currents
    plotted.set_ylim(0, 100)

    # Set the color of the axis labels and ticks
    plotted.spines['bottom'].set_color('#C65D3B')
    plotted.spines['top'].set_color('#C65D3B')
    plotted.spines['right'].set_color('#C65D3B')
    plotted.spines['left'].set_color('#C65D3B')
    plotted.xaxis.label.set_color('#C65D3B')
    plotted.yaxis.label.set_color('#C65D3B')
    plotted.tick_params(axis='x', colors='white')
    plotted.tick_params(axis='y', colors='white')

    canvas = FigureCanvasTkAgg(fig, master = app)   
    canvas.draw() 
    canvas.get_tk_widget().place(relx=0.65, rely=0.14) 
    toolbar = NavigationToolbar2Tk(canvas, app) 
    toolbar.update() 
    canvas.get_tk_widget().place(relx=0.65, rely=0.14) 
    
    app.after(DEFAULT_UPDATE_RATE, lambda: update_plot(plotted, "beta"))

# --------------------------------------------------------------------------------------------------------- #

# This function is called when the user switches between plotting the current and the temperature.
# It simply switches the data the plots access to plot the correct data.
def switch_plot_alpha():
    global y_alpha
    data_to_plot = alpha_plot_data.get()
    if (data_to_plot == "Current"):
        y_alpha = tf_current_data_received
    elif (data_to_plot == "Temperature"):
        y_alpha = temperature_data
    
# This function is the same as switch_plot_alpha, except it is for the beta plot.
def switch_plot_beta():
    global y_beta
    data_to_plot = beta_plot_data.get()
    if (data_to_plot == "Current"):
        y_beta = tf_current_data_received
    elif (data_to_plot == "Temperature"):
        y_beta = temperature_data

# --------------------------------------------------------------------------------------------------------- #

# This function is called when the user inputs 'pressure test'. It sets up a listening socket to receive
# the pressure data from the pynq, then displays it on the GUI. It will constantly update the pressure data
# until the program ends.
#
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
            pressure_value_label.config(text=decoded_lsp)

# --------------------------------------------------------------------------------------------------------- #

# This function is called every 0.1 seconds to check if the threads are still running.
def check_threads():
    global app
    if not tf_current_data_thread.is_alive() and not temperature_data_thread.is_alive():
        app.destroy()
    else:app.after(100, check_threads)
    
# --------------------------------------------------------------------------------------------------------- #

# This function is called at the beginning, creating the database for the listbox.
#
# def create_database():
#     conn = sqlite3.connect("data/names.db")
#     c = conn.cursor()

#     c.execute("""CREATE TABLE IF NOT EXISTS names (id INTEGER PRIMARY KEY,name TEXT)""")
#     conn.commit()
#     conn.close()

# This function is also called at the beginning and when the user inputs the 'clear' command. It empties the database
# and updates the listbox to show that it is empty.
#
def clearDB():
    conn = sqlite3.connect("data/names.db")
    c = conn.cursor()

    c.execute("DELETE FROM names")

    conn.commit()
    conn.close()

    update_listbox()

# --------------------------------------------------------------------------------------------------------- #

# Ends the threads and closes the program.
#
def exit():
    global running
    running = 0
    check_threads()

# --------------------------------------------------------------------------------------------------------- #

# Programs title
#
app = tk.Tk()
app.title("AtomCraft Controller")
app.geometry("1440x900")


# --------------------------------------------------------------------------------------------------------- #

# Making program frames

# for 1440x900 res
plot_frame = tk.Frame(app, width=10000, height=695, bg="#1D1D1D", bd=1, relief="solid")
plot_frame.place(relx=0.21, rely=0)

left_frame = tk.Frame(app, width=320, height=695, bg="#005B5C", bd=1, relief="solid")
left_frame.place(relx=0, rely=0)

bottom_frame = tk.Frame(app, width=1920, height=485, bg="#005B5C", bd=1, relief="solid")
bottom_frame.place(relx=0, rely=0.644)

# --------------------------------------------------------------------------------------------------------- #
# Dividing lines

canvas = tk.Canvas(app, width=1.5, height=300, bg="#C65D3B", highlightthickness=0)
canvas.place(relx=0.249, rely=0.644)
canvas.create_line(1, 579, 1, 900, fill="black")

canvas2 = tk.Canvas(app, width=1.5, height=300, bg="#C65D3B", highlightthickness=0)
canvas2.place(relx=0.5, rely=0.644)
canvas2.create_line(1, 579, 1, 900, fill="black")

canvas2 = tk.Canvas(app, width=1.5, height=300, bg="#C65D3B", highlightthickness=0)
canvas2.place(relx=0.75, rely=0.644)
canvas2.create_line(1, 579, 1, 900, fill="black")

canvas2 = tk.Canvas(app, width=2000, height=1.5, bg="#C65D3B", highlightthickness=0)
canvas2.place(relx=0, rely=0.644)
canvas2.create_line(1, 579, 1, 900, fill="black")

canvas2 = tk.Canvas(app, width=1.5, height=511, bg="#C65D3B", highlightthickness=0)
canvas2.place(relx=0.22, rely=0)
canvas2.create_line(1, 1, 1.5, 695, fill="black")

# --------------------------------------------------------------------------------------------------------- #


# just a simple label

entry = tk.Entry(left_frame, highlightbackground='#005B5C')
entry.place(relx=0.20, rely=0.05) 

pressure_title = tk.Label(app, text="Pressure", font=("Verdana", 20), background='#060621', bd=2, relief="solid")
pressure_title.place(relx=0.102, rely=0.70)

pressure_value_label = tk.Label(app, text="0.00", font=("Verdana", 48), background='#060621', bd=2, relief="solid")
pressure_value_label.place(relx=0.095, rely=0.75)

number_label2_title = tk.Label(app, text="Measurement 2", font=("Verdana", 20), background='#060621', bd=2, relief="solid")
number_label2_title.place(relx=0.33, rely=0.70)

number_label2 = tk.Label(app, text="0.00", font=("Verdana", 48), background='#060621')
number_label2.place(relx=0.345, rely=0.75)

number_label3_title = tk.Label(app, text="Measurement 3", font=("Verdana", 20), background='#060621', bd=2, relief="solid")
number_label3_title.place(relx=0.581, rely=0.70)

number_label3 = tk.Label(app, text="0.00", font=("Verdana", 48), background='#060621')
number_label3.place(relx=0.595, rely=0.75)

number_label4_title = tk.Label(app, text="Measurement 4", font=("Verdana", 20), background='#060621', bd=2, relief="solid")
number_label4_title.place(relx=0.83, rely=0.70)

number_label4 = tk.Label(app, text="0.00", font=("Verdana", 48), background='#060621')
number_label4.place(relx=0.845, rely=0.75)

# --------------------------------------------------------------------------------------------------------- #

# All dropdown menus for the graphs (both alpha and beta)
#
alpha_dd_menu = ["Current", "Temperature"]

# dd for plot_alpha
alpha_plot_data = tk.StringVar()
alpha_plot_data.set("Select Variable To Plot") 
alpha_plot_data.trace_add("write", lambda *args: switch_plot_alpha())

alpha_dropdown = tk.OptionMenu(app, alpha_plot_data, *alpha_dd_menu)

alpha_dropdown.config(activebackground="lightgrey", bg="#1D1D1D", activeforeground="black", fg="white")

alpha_dropdown.place(relx=0.3, rely=0.1) 
plot_alpha()

# --------------------------------------------------------------------------------------------------------- #

beta_dd_menu = ["Current", "Temperature"]

# dd for plot_alpha
beta_plot_data = tk.StringVar()
beta_plot_data.set("Select Variable To Plot") 
beta_plot_data.trace_add("write", lambda *args: switch_plot_beta())

beta_dropdown = tk.OptionMenu(app, beta_plot_data, *beta_dd_menu)

beta_dropdown.config(activebackground="lightgrey", bg="#1D1D1D", activeforeground="black", fg="white")

beta_dropdown.place(relx=0.65, rely=0.1) 

plot_beta()

# --------------------------------------------------------------------------------------------------------- #

# Initialises the database and listbox, and binds the enter key to the on_submit function
#
create_database()
listbox = tk.Listbox(left_frame, height=25, width=33)
listbox.place(relx=0.028, rely=0.1)
update_listbox()

app.bind('<Return>', on_submit)

# --------------------------------------------------------------------------------------------------------- #

# Exit button for the GUI
#
exit_button = tk.Button(app, text="Exit (gracefully)", command = exit, highlightbackground='#1D1D1D')
exit_button.place(relx=0.9, rely=0.025) 

# --------------------------------------------------------------------------------------------------------- #

def handle_pynq_commands():
    pass

# --------------------------------------------------------------------------------------------------------- #

# List of commands that the user can input (This will be updated as more integrations are added)
#
commands = {
    "clear": clearDB,
    "start control loop": prompt_for_waveform,
    "temperature test": handle_pynq_commands,
    "pressure test": handle_pynq_commands,
}

def handle_command(command):
    if command in commands:
        commands[command]()
    else:
        add_to_db("Invalid command")

# --------------------------------------------------------------------------------------------------------- #

# Main function that creates and starts the threads, then starts the GUI
#
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


        