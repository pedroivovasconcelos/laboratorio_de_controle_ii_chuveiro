import time

from board_controller import BoardController
from loads_threads import Loads
from statistics import Statistics


if __name__ == '__main__':
    # Parâmetros base
    set_point = 6
    nanoseconds_to_seconds = 1000000000  # Quantos Nanosegundos existem em um segundo
    sampling_time = 400000  # Tempo entre amostras
    number_of_samples = 10000
    samples_per_second = float(nanoseconds_to_seconds / sampling_time)
    rt_priority = 90

    # Inicia a classe do controlador e dos loads
    board_controller = BoardController(set_point=set_point,
                                       sampling_time=sampling_time,
                                       samples_per_second=samples_per_second,
                                       number_of_samples=number_of_samples,
                                       rt_priority=rt_priority)
    loads = Loads(board_controller)
    statistics_of_process = Statistics(board_controller)

    board_controller.start()
    loads.start()

    time.sleep((sampling_time*number_of_samples/nanoseconds_to_seconds)+1)
    statistics_of_process.caculate_stats()
    statistics_of_process.store_stats()
