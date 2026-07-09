import pyvisa

class BaseInstrument:
    def __init__(self, resource_string, name, timeout_ms=10000):
        self.name = name
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(resource_string)
        self.inst.timeout = timeout_ms
        self.inst.write_termination = '\n'
        self.inst.read_termination = '\n'

    def reset(self):
        self.inst.write('*RST')

    def identify(self):
        return self.inst.query('*IDN?').strip()

    def check_errors(self):
        return self.inst.query('SYST:ERR?').strip()

    def close(self):
        self.inst.close()