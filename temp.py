import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import numpy as np

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.create_widgets()

    def create_widgets(self):
        fig = plt.figure(figsize=(4, 4))
        ax = plt.axes((0.1, 0.1, 0.8, 0.8), polar=True)
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid(row=0, column=1)

        plotbutton = tk.Button(self, text="plot", command=lambda: self.auto_plot(ax))
        plotbutton.grid(row=0, column=0)


    def auto_plot(self, ax):
        c = ['r', 'b', 'g']
        for _ in range(5):
            ax.clear()

            for i in range(3):
                theta = np.random.uniform(0, 360, 10)
                r = np.random.uniform(0, 1, 10)
                plt.polar(theta, r, linestyle="None", marker='o', color=c[i])
                plt.draw()

                self.after(500) # display plot keeping button responsive
                self.update() # redraw plot


Application().mainloop()