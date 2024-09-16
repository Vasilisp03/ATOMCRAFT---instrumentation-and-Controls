import sqlite3
import threading
import tkinter as tk

def update_plot():
    global plot1
    global y
    y = data_received
    smoothed_y = savgol_filter(y, 7, 2)
    plot1.clear()
    plot1.plot(y, label = 'raw signal', color = 'blue')
    plot1.plot(smoothed_y, label = 'smoothed signal', color = 'red') 
    plot1.figure.canvas.draw_idle()
    
    app.after(PLOT_UPDATE_RATE, update_plot)

# --------------------------------------------------------------------------------------------------------- #

def plot():
    global plot1
    global y
    fig = Figure(figsize = (8, 5), dpi = 100) 
    y = data_received
    smoothed_y = savgol_filter(y, 7, 2)
    plot1 = fig.add_subplot(111) 
    plot1.plot(y, label = 'raw signal', color = 'blue')
    plot1.plot(smoothed_y, label = 'smoothed signal', color = 'red') 
    plot1.set_xlim(0, len(y))
    plot1.set_ylim(min(y), max(y))
    canvas = FigureCanvasTkAgg(fig, master = app)   
    canvas.draw() 
    canvas.get_tk_widget().pack() 
    toolbar = NavigationToolbar2Tk(canvas, app) 
    toolbar.update() 
    canvas.get_tk_widget().pack()
    
    app.after(PLOT_UPDATE_RATE, update_plot)

# --------------------------------------------------------------------------------------------------------- #

def check_threads():
    global app
    if not receive_data.is_alive():
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

# if __name__ == "__main__":
#     # set up all threads that we want to exist
#     receive_data = threading.Thread(target = receive_from_pynq)

#     # start threads running
#     receive_data.start()
    
#     # start app window
#     app.mainloop()


        