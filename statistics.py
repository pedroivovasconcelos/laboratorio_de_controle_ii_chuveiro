import numpy as np
import pandas as pd
import scipy.stats as stats

from board_controller import BoardController


class Statistics:
    """Realiza os cálculos para imprimir na tela, gravar e plotar"""

    def __init__(self, board_controller: BoardController, time_filename: str = "Tempo.csv"):
        self.board_controller = board_controller
        self.time_filename = time_filename

    def caculate_stats(self):
        """O código original está diferente deste, porque não cheguei a uma conclusão
        do raciocínio original. A implementação abaixo está correta considerando
        os tempos coletados"""
        mean = np.mean(a=self.board_controller.start_cycle)
        median = np.median(a=self.board_controller.start_cycle)
        standard_deviation = np.std(a=self.board_controller.start_cycle)
        mean_latency = np.mean(a=self.board_controller.end_cycle)
        median_latency = np.median(a=self.board_controller.end_cycle)
        # Também conhecido como MAD, Com a fórmula:
        # MAD = (1/n) * ∑|xi - X̄|
        # E o código:
        # mean(absolute(data - mean(data)))
        mean_absolute_deviation = stats.median_abs_deviation(x=self.board_controller.start_cycle)

        print(f"Media: {mean}\n"
              f"Mediana: {median}\n"
              f"Desvio padrão: {standard_deviation}\n"
              f"Latência Média: {mean_latency}\n"
              f"Latência Mediana: {median_latency}\n"
              f"Desvio Absoluto Médio: {mean_absolute_deviation}")

    def store_stats(self):
        data = {"Início do Ciclo": self.board_controller.start_cycle,
                "Tempo em execução": self.board_controller.end_cycle}
        df = pd.DataFrame(data)
        df.to_csv(self.time_filename, index=False)
