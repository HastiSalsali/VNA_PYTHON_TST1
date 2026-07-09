from RsInstrument import RsInstrument
from instruments.base_instrument import BaseInstrument

VNA_NAME = 'ZNA26'

class VNA:
    def __init__(self, resource_string, timeout_ms=10000):
        self.inst = RsInstrument(resource_string, id_query=False, reset=False)
        self.inst.visa_timeout = timeout_ms
        self.inst.instrument_status_checking = True

    # override base methods to use RsInstrument's API
    def reset(self):
        self.inst.reset()

    def identify(self):
        return self.inst.idn_string

    def check_errors(self):
        return self.inst.query_all_errors()
    
    # ── Configuration ────────────────────────────────────────────
    def set_cw_mode(self, freq_hz):
        self.inst.write_str(f'SENS:SWE:TYPE CW')
        self.inst.write_float('SENS:FREQ:CW ', freq_hz)

    def set_sweep_points(self, n=200):
        self.inst.write_int('SENS:SWE:POIN ', n)

    def set_power(self, dbm=-10):
        self.inst.write_float('SOUR:POW ', dbm)

    S_PARAMETERS = ('S11', 'S12', 'S21', 'S22')

    def set_sparam(self, sparam, trace_name='Trc1'):
        sparam = sparam.upper()
        if sparam not in self.S_PARAMETERS:
            raise ValueError(f"sparam must be one of {self.S_PARAMETERS}, got {sparam!r}")
        self.inst.write_str(f"CALC:PAR:SDEF '{trace_name}', '{sparam}'")
        self.inst.write_str(f"CALC:PAR:SEL '{trace_name}'")

    def set_if_bandwidth(self, hz=1000):
        self.inst.write_float('SENS:BAND ', hz)

    # ── Measurement ──────────────────────────────────────────────
    def trigger_sweep(self, timeout_ms=15000):
        #self.inst.write_str('SENS:SWE:MODE SING') #single sweep
        #self.inst.write_with_opc('INIT:IMM', timeout_ms) 
        self.inst.write_str('INIT:CONT OFF')
        self.inst.write_with_opc('INIT:IMM', timeout_ms)

    def _get_trace_complex(self):
        raw = self.inst.query_bin_or_ascii_float_list('CALC:DATA? SDAT') #Unformatted trace data: real and imaginary part of each measurement point. 
        real = raw[0::2]
        imag = raw[1::2]
        return [complex(r, i) for r, i in zip(real, imag)]

    def get_frequencies(self):
        return self.inst.query_bin_or_ascii_float_list('SENS:FREQ:DATA?')

    # ── Status ───────────────────────────────────────────────────
    def is_sweeping(self):
        return self.inst.query_int('SENS:SWE:MODE?') != 0

    def measure_sparam_cw_over_time(self, sparam, freq_hz, num_points=50,
                                     power_dbm=-10, if_bandwidth_hz=1000):
        self.set_cw_mode(freq_hz)
        self.set_sweep_points(num_points)
        self.set_power(power_dbm)
        self.set_if_bandwidth(if_bandwidth_hz)
        self.set_sparam(sparam)

        self.trigger_sweep()
        sparam_values = self._get_trace_complex()

        sweep_time_s = self.inst.query_float('SENS:SWE:TIME?')
        elapsed_times = [i * sweep_time_s / num_points for i in range(num_points)]

        return elapsed_times, sparam_values
    
    def close(self):
        self.inst.close()
    
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        try:
            self.close()
        except:
            pass