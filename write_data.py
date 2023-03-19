import csv


class WriteData:
    """Classe responsável por gravar dados nos arquivos."""

    def __init__(self, filename: str, header: list = None):
        """Armazena o nome do arquivo e grava um cabeçalho caso seja preenchido"""
        self.filename = filename
        if header:
            with open(self.filename, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(header)

    def write_one_row_to_csv(self, data: list):
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)

    def write_data_to_csv(self, data: list[list]):
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)