import tkinter as tk
import sqlite3

def clear():
    conn = sqlite3.connect("data/names.db")
    c = conn.cursor()

    c.execute("DELETE FROM names")

    conn.commit()
    conn.close()

    update_listbox()



def create_database():
    conn = sqlite3.connect("data/names.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS names (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )""")
    conn.commit()
    conn.close()

create_database()

def on_submit():
    name = entry.get()
    conn = sqlite3.connect("data/names.db")
    c = conn.cursor()

    c.execute("INSERT INTO names (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

    update_listbox()

def update_listbox():
    conn = sqlite3.connect("data/names.db")
    c = conn.cursor()

    c.execute("SELECT * FROM names")
    rows = c.fetchall()

    listbox.delete(0, tk.END)
    for row in rows:
        listbox.insert(tk.END, row[1])

    conn.close()

# programs title
app = tk.Tk()
app.title("AtomCraft Controller")
app.geometry("1280x720")

# just a simple label
label = tk.Label(app, text="Enter your name:")
label.pack()

entry = tk.Entry(app)
entry.pack()

# list of whatever
listbox = tk.Listbox(app)
listbox.pack()
update_listbox()

# simple button to submit whatever
submit_button = tk.Button(app, text="Submit", command=on_submit)
submit_button.pack()

clear_data_button = tk.Button(app, text="Clear data", command=clear)
clear_data_button.pack()


app.mainloop()
    