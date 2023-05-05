import os
import threading
import time
from ctypes import c_long
import nidaqmx
import numpy as np
from real_time_screen import ControllerWindow


class BoardController:
    def __init__(self, set_point: int, sampling_time: int, samples_per_second: float, number_of_samples: int,
                 rt_priority: int, ):
        """
        Construtor responsável por criar duas tarefas para ler e gravar na placa.
        É necessário definir quais as portas a serem utilizadas.
        Parameters:
        set_point: int
        number_of_samples: int
        samples_per_second: int
        sampling_time: int
        rt_priority: int
        """
        self.sampling_time = sampling_time
        self.samples_per_second = samples_per_second
        self.number_of_samples = number_of_samples
        self.rt_priority = rt_priority
        self.set_point = set_point
        self.period_ns = self.sampling_time
        self.start_time = time.monotonic_ns()
        self.next_period = self.start_time

        self.voltage_read = 0
        self.voltage_set = 0
        self.board_window = ControllerWindow(voltage_read=self.voltage_read,
                                             voltage_set=self.voltage_set)
        self.board_window.run()

        self.start_cycle = np.zeros(number_of_samples, dtype=c_long)
        self.end_cycle = np.zeros(number_of_samples, dtype=c_long)
        self.count = 0

        self.ai_task_handle = None
        self.ao_task_handle = None

    def start(self):
        """Inicia todas as threads e as encerra quando acabar o ciclo."""
        self.ai_task_handle = nidaqmx.Task()
        self.ai_task_handle.ai_channels.add_ai_voltage_chan("Dev1/ai0")
        self.ai_task_handle.timing.cfg_samp_clk_timing(
            rate=self.samples_per_second,
            sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
            samps_per_chan=self.number_of_samples,
        )

        self.ao_task_handle = nidaqmx.Task()
        self.ao_task_handle.ao_channels.add_ao_voltage_chan("Dev1/ao0")
        self.ao_task_handle.timing.cfg_samp_clk_timing(
            rate=self.samples_per_second,
            sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
            samps_per_chan=self.number_of_samples,
        )

        rt_thread = threading.Thread(target=self.real_time_loop, daemon=True)
        rt_thread.start()
        rt_thread.join()

    def real_time_loop(self):
        """Método responsável por ler e gravar dados da placa.
        Sugestão de desafio: Como ler e gravar na placa de maneira indepedente e concorrente?"""
        # Define a pioridade da task
        thread_parameters = os.sched_param(self.rt_priority)
        os.sched_setscheduler(0, os.SCHED_FIFO, thread_parameters)

        self.ai_task_handle.start()
        self.ao_task_handle.start()

        while self.count < self.number_of_samples:
            time_before_task = time.time_ns() // 1000
            self.do_real_time_task()
            self.start_cycle[self.count] = time_before_task
            self.end_cycle[self.count] = time_before_task - (time.time_ns() // 1000)
            self.count += 1
            # Aguarda até o final do período
            self.wait_rest_of_period()

    def do_real_time_task(self):
        self.voltage_read = self.ai_task_handle.read()
        self.voltage_set = self.board_window.voltage_slider.get()
        self.ao_task_handle.write(self.voltage_set)
        self.board_window.run_time.append((time.monotonic_ns() - self.start_time) / 1e6)
        self.board_window.voltage_read_history.append(self.voltage_read)
        self.board_window.voltage_set_history.append(self.voltage_set)

    def get_time_left(self):
        return (self.next_period - time.monotonic_ns()) / 1e9

    def inc_period(self):
        self.next_period += self.sampling_time

    def wait_rest_of_period(self):
        self.inc_period()
        time_left = self.get_time_left()
        time.sleep(time_left)
