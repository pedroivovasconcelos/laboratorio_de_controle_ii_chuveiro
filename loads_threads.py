import datetime
import math
import threading
from shower import BoardController
from write_data import WriteData


class Loads:
    def __init__(self, board_controller: BoardController):
        self.board_controller = board_controller

    def start(self):
        process_load_thread = threading.Thread(target=self.load_processing, daemon=True)
        load_file_thread = threading.Thread(target=self.load_file, daemon=True)

        process_load_thread.start()
        load_file_thread.start()

        process_load_thread.join()
        load_file_thread.join()

    def load_file(self):
        """Salva dados no arquivo de load com informações do processo"""
        write_load_file = WriteData(filename="thread_load_file.csv",
                                    header=["Output", "Input", "Operation Mode", "Setpoint", "Last time loaded",
                                            "Time sleeped"])
        last_load_time = datetime.datetime.now()
        while True:
            time_slept = datetime.datetime.now()
            data_to_write = [self.board_controller.voltage_read, self.board_controller.voltage_set, "Simulation",
                             self.board_controller.set_point, last_load_time,
                             time_slept]
            write_load_file.write_one_row_to_csv(data=data_to_write)
            print(f"data appended:{data_to_write}")
            last_load_time = datetime.datetime.now()

    @staticmethod
    def load_processing():
        print("Start Processing.")
        while True:
            pow(2, math.exp(5))
            print("End Processing.")
