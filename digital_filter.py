import numpy as np
from scipy.signal import lfilter


class DigitalFilter:
    def __init__(self, signal: np.ndarray, cutoff_freq: float, sample_rate: float):
        """
        Classe responsável por gerar sinais filtrados do sistema
        Parametros
        signal: Sinal em um array do tipo numpy
        cutoff_freq: Frequência de corte estabelescida por 1/(pólo)
        sample_rate: Taxa de amostragem do processo
        """
        self.signal = signal
        self.cutoff_freq = cutoff_freq
        self.sample_rate = sample_rate
        self.filtered_signal = None
        self.prev_output = None

        # Calcula o coeficiente alpha se não foi calculado
        RC = 1.0 / (2 * 3.14159 * self.cutoff_freq)
        dt = 1.0 / self.sample_rate
        self.alpha = dt / (RC + dt)

    def first_order_low_pass(self) -> np.ndarray:
        """
        Filtro de ruído de sinais de primeira ordem.
        :return: Retorna o sinal filtrado em um array
        """
        # Calculate filter coefficient alpha if it hasn't been calculated yet
        if self.alpha is None:
            RC = 1.0 / (2 * 3.14159 * self.cutoff_freq)
            dt = 1.0 / self.sample_rate
            self.alpha = dt / (RC + dt)

        # Apply filter to input signal
        for x in self.signal:
            if self.prev_output is None:
                y = x
            else:
                y = self.alpha * x + (1 - self.alpha) * self.prev_output
            self.prev_output = y
            self.filtered_signal.append(y)
        return self.filtered_signal

    def iir_filter(self, input_signal: list):
        pass


# # Example usage
# import numpy as np
# import matplotlib.pyplot as plt
#
# # Generate a test signal
# t = np.linspace(0, 1, 1000, endpoint=False)
# signal = np.sin(2*np.pi*10*t) + 0.5*np.sin(2*np.pi*20*t)
#
# # Apply a first-order low-pass filter
# cutoff_freq = 15  # Hz
# sample_rate = 1000  # Hz
# filter_obj = FirstOrderLowPassFilter(cutoff_freq, sample_rate)
# filtered_signal = filter_obj.apply(signal)
#
# # Plot the original and filtered signals
# plt.plot(t, signal, label='Original')
# plt.plot(t, filtered_signal, label='Filtered')
# plt.legend()
# plt.show()

# class FirstOrderLowPassFilter:
#     def __init__(self, cutoff_freq, sample_rate):
#         self.cutoff_freq = cutoff_freq
#         self.sample_rate = sample_rate
#         self.alpha = None
#         self.prev_output = None
#
#     def apply(self, input_signal):
#         # Calculate filter coefficient alpha if it hasn't been calculated yet
#         if self.alpha is None:
#             RC = 1.0 / (2 * 3.14159 * self.cutoff_freq)
#             dt = 1.0 / self.sample_rate
#             self.alpha = dt / (RC + dt)
#
#         # Apply filter to input signal
#         output_signal = []
#         for x in input_signal:
#             if self.prev_output is None:
#                 y = x
#             else:
#                 y = self.alpha * x + (1 - self.alpha) * self.prev_output
#             self.prev_output = y
#             output_signal.append(y)
#         return output_signal