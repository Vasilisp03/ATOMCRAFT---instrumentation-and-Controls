# plan here is to write python code that will recieve the sockets sent from the pynq and then.
# if that is able to recieve quickly then we can use that in the controller.py file to actually
# create a nice bit of software.

import sys
from socket import *
import threading
import time
from collections import defaultdict
import tkinter as tk
import sqlite3

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

    # proccess data this is not right just very placeholder
    while True:
        msg, c_add = s_sock.recvfrom(1024)
        decoded_lsp = msg.decode()
        print(f"\n+received {decoded_lsp}")

        data_received.append(decoded_lsp)

# --------------------------------------------------------------------------------------------------------- #

# this is code for the pynq probably that is sending packets, however can be used here to send
# information for control actually (may or may not work). Again just copied my own old code
# will need restructuring to do what we want it to.
def send_instructions(command):
    c_sock = socket(AF_INET, SOCK_DGRAM)
    print("-sending",command)
    packet = command.encode()
    send_address = (HOST, ROUTER_PORT)
    c_sock.sendto(packet, send_address)

# --------------------------------------------------------------------------------------------------------- #

def clear():
    conn = sqlite3.connect("names.db")
    c = conn.cursor()

    c.execute("DELETE FROM names")

    conn.commit()
    conn.close()

    update_listbox()

# --------------------------------------------------------------------------------------------------------- #

def create_database():
    conn = sqlite3.connect("names.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS names (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )""")
    conn.commit()
    conn.close()

# --------------------------------------------------------------------------------------------------------- #

def on_submit():
    name = entry.get()
    send_instructions(name)
    conn = sqlite3.connect("names.db")
    c = conn.cursor()

    c.execute("INSERT INTO names (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

    update_listbox()

# --------------------------------------------------------------------------------------------------------- #

def update_listbox():
    conn = sqlite3.connect("names.db")
    c = conn.cursor()

    c.execute("SELECT * FROM names")
    rows = c.fetchall()

    listbox.delete(0, tk.END)
    for row in rows:
        listbox.insert(tk.END, row[1])

    conn.close()

# --------------------------------------------------------------------------------------------------------- #

# programs title
app = tk.Tk()
app.title("AtomCraft Controller")
app.geometry("1280x720")

# just a simple label
label = tk.Label(app, text="Enter anything")
label.pack()

entry = tk.Entry(app)
entry.pack()

# list of whatever
listbox = tk.Listbox(app)
listbox.pack()
update_listbox()

# simple button to submit whatever
submit_button = tk.Button(app, text="send packet", command=on_submit)
submit_button.pack()

clear_data_button = tk.Button(app, text="Clear data", command=clear)
clear_data_button.pack()


# --------------------------------------------------------------------------------------------------------- #

if __name__ == "__main__":

    # set up all threads that we want to exist
    recieve_data = threading.Thread(target=receive_from_pynq)
    send_command = threading.Thread(target = send_instructions, args = ())

    create_database()
    app.mainloop()

    # start threads running
    try:
        recieve_data.start()
        time.sleep(1)
        send_command.start()

    except KeyboardInterrupt:
        recieve_data.join()
        send_command.join()

        