class PIcontroller:
    def __init__(self, kp, ti, td, ts):
        self.kp = kp
        self.kpp = self.kp*(1+ts/())
