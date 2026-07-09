import numpy as np
import matplotlib.pyplot as plt
import pyvisa

from instruments.vna import VNA

RESOURCE_STRING = 'USB0::0x0AAD::0x0198::101157::INSTR'  # replace


def run_s11_sweep():
    vna = None

    try:
        vna = VNA(RESOURCE_STRING)

        print(vna.identify())


        elapsed_times, s11_values = vna.measure_sparam_cw_over_time(
            'S11',
            freq_hz=1.9e9,
            num_points=200,
            power_dbm=0,
            if_bandwidth_hz=10000,
        )
        
    finally:
        if vna is not None:
            vna.close()

    s11_values = np.array(s11_values)
    s11_magnitudes = np.abs(s11_values)
    phase_deg = np.angle(s11_values, deg=True)

    fig, (ax_mag, ax_phase) = plt.subplots(2, 1, sharex=True)

    ax_mag.plot(elapsed_times, s11_magnitudes, marker='o')
    ax_mag.set_ylabel('|S11|')
    ax_mag.set_title('S11 vs Time (CW)')
    ax_mag.grid(True)

    ax_phase.plot(elapsed_times, phase_deg, marker='o')
    ax_phase.set_xlabel('Elapsed time (s)')
    ax_phase.set_ylabel('Phase (deg)')
    ax_phase.grid(True)

    plt.tight_layout()
    plt.show()


def print_devices():
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()

    if not resources:
        print('No VISA devices found.')
        return

    print(f'Found {len(resources)} VISA device(s):\n')
    for resource_string in resources:
        try:
            inst = rm.open_resource(resource_string)
            idn = inst.query('*IDN?').strip()
            inst.close()
        except pyvisa.VisaIOError as e:
            idn = f'<could not query *IDN? — {e}>'

        print(f'  Resource: {resource_string}')
        print(f'  IDN:      {idn}')
        print('-' * 60)


def main():
    print('VNA Test Menu')
    print('  1) Run S11 sweep')
    print('  2) Print connected devices')
    choice = input('Select an option: ').strip()

    if choice == '1':
        run_s11_sweep()
    elif choice == '2':
        print_devices()
    else:
        print(f'Invalid option: {choice!r}')


if __name__ == '__main__':
    main()
