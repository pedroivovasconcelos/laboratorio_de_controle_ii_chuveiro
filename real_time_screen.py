# import everything from tkinter module
import math
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
        width_px, height_px = 800, 600
        dpi = 100
        width_in = width_px / dpi
        height_in = height_px / dpi
        self.fig = plt.figure(figsize=(width_in, height_in), dpi=100)
        canvas = FigureCanvasTkAgg(self.fig, master=self.controller_window)
        canvas.get_tk_widget().grid(column=0, row=1)
        self.fig.subplots(1, 1)
        self.ani = FuncAnimation(self.fig, self.animate, interval=200, blit=False, save_count=1000000)
        self.voltage_slider = Scale(self.controller_window, from_=0.0, to=10.0, length=800, tickinterval=0.1,
                                    orient=HORIZONTAL)
        self.voltage_slider.grid(column=0, row=2)
        self.voltage_slider.set(8.0)

    def animate(self, _):
        ax1 = self.fig.get_axes()[0]
        ax1.cla()
        ax1.plot(self.run_time, self.voltage_set_history, label='Voltage Set', color='blue')
        ax1.plot(self.run_time, self.voltage_read_history, label='Voltage Read', color='red')
        ax1.set_ylim(0, 10)

        if self.run_time[-1] <= 10:
            ax1.set_xlim(0, 10)
        else:
            ax1.set_xlim(0, math.ceil(self.run_time[-1]))
        ax1.set_xlabel('Time (s)')
        ax1.legend(loc='upper right')

    def animate_test(self, _):
        """
        Para testes, use este método no FuncAnimation
        """
        current_time = (time.monotonic_ns() - self.start_time) / 1e9
        self.run_time.append(current_time)
        self.voltage_set_history.append(self.voltage_slider.get())
        self.voltage_read_history.append(random.uniform(0, 10))
        ax1 = self.fig.get_axes()[0]
        ax1.cla()
        ax1.plot(self.run_time, self.voltage_set_history, label='Voltage Set', color='blue')
        ax1.plot(self.run_time, self.voltage_read_history, label='Voltage Read', color='red')
        ax1.set_ylim(0, 10)

        if current_time <= 10:
            ax1.set_xlim(0, 10)
        else:
            ax1.set_xlim(0, math.ceil(current_time))
        ax1.set_xlabel('Time (s)')
        ax1.legend(loc='upper right')

    def run(self):
        self.controller_window.mainloop()
        plt.show()


if __name__ == '__main__':
    c_window = ControllerWindow()
    c_window.run()
