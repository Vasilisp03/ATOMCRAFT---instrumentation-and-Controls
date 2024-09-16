import pc_frontend
import pc_receiver
import pynq_receiver
import sqlite3
import threading
import tkinter as tk

if __name__ == "__main__":
    # set up all threads that we want to exist
    receive_data = threading.Thread(target = pc_receiver.receive_from_pynq)

    # start threads running
    receive_data.start()
    
    # start app window
    pc_frontend.app.mainloop()