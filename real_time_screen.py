# import everything from tkinter module
import random
import time
from tkinter import *

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ControllerWindow:
    def __init__(self, voltage_read: float = 0.0, voltage_set: float = 0.0):
        self.start_time = time.monotonic_ns()
        self.run_time = [0.0]  # Tempo em milisegundos
        self.voltage_read_history = [voltage_read]
        self.voltage_set_history = [voltage_set]

        self.controller_window = Tk(className="Controlador de chuveiro")
        self.controller_window.state("zoomed")

        Label(self.controller_window, text="Controlador de chuveiro com mostrador"
                                           " em tempo real de temperatura e log").grid(column=0, row=0)
        plt.style.use('fivethirtyeight')
        canvas = FigureCanvasTkAgg(plt.gcf(), master=self.controller_window)
        canvas.get_tk_widget().grid(column=0, row=1)
        plt.gcf().subplots(1, 2)
        self.ani = FuncAnimation(plt.gcf(), self.animate2, interval=1000, blit=False)
        self.voltage_slider = Scale(self.controller_window, from_=0.0, to=10.0, length=800, tickinterval=0.1,
                                    orient=HORIZONTAL)
        self.voltage_slider.grid(column=0, row=2)
        self.voltage_slider.set(8.0)

    def animate(self):
        ax1, ax2 = plt.gcf().get_axes()
        ax1.cla()
        ax2.cla()
        ax1.plot(self.run_time, self.voltage_set_history)
        ax2.plot(self.run_time, self.voltage_read_history)

    def animate2(self, _):
        self.run_time.append((time.monotonic_ns() - self.start_time) / 1e9)
        self.voltage_read_history.append(random.randint(0, 10))
        self.voltage_set_history.append(self.voltage_slider.get())
        ax1, ax2 = plt.gcf().get_axes()
        ax1.cla()
        ax2.cla()
        ax1.plot(self.run_time, self.voltage_set_history)
        ax2.plot(self.run_time, self.voltage_read_history)

    def run(self):
        self.controller_window.mainloop()
        plt.show()


if __name__ == '__main__':
    c_window = ControllerWindow()
    c_window.run()
