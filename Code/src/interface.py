import serial
import serial.tools.list_ports
import csv
import sys
import time
import datetime
import readline
import math
from collections import deque

def input_with_preset(prompt, preset):
    readline.set_startup_hook(lambda: readline.insert_text(preset))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()

def hard_reset_mega(ser):
    print("Sending hard reset command to Mega...")
    # Drop DTR line to trigger hardware reset
    ser.dtr = False
    time.sleep(0.1)
    
    # Bring it back up to let the board boot up normally
    ser.dtr = True
    time.sleep(1.0) # Give the Mega a second to run its setup() routine
    # print("Mega successfully restarted!")

def list_active_ports():
    # Fetch all available serial ports\
    default = None
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("No connected serial devices found.")
        return

    print("Connected Serial Ports:")
    print("-" * 80)

    for port in ports:
        # port.device is the name (e.g., COM3 or /dev/ttyUSB0)
        # port.description is the device name given by the OS
        if port.hwid != 'n/a':
            print(f"Port: {port.device}")
            print(f"Description: {port.description}")
            print(f"Hardware ID: {port.hwid}")
            print("-" * 80)
            if default is None:
                default = port.device

    return default

print("")
print('=' * 80)
print("""                        ____  _   _  _____ ______ _   _ 
                      /  ___|| | | ||_   _||  ___| | | |
                      \ `--. | |_| |  | |  | |_  | | | |
                       `--. \|  _  |  | |  |  _| | | | |
                      /\__/ /| | | |__| |__| |_  | |_| |
                      \____(_)_| |_(_)___(_)_(_)  \___/      
""")
print('=' * 80)
print("                  SHIFU - Sensing Heat & Intense Fluid Uh-ohs                   ")
print('-' * 80)
print('***                     GNU General Public License 2.0                       ***')
print('=' * 80)
# listing active ports
default_dev = list_active_ports()
default_baud = 115200
default_name = f'output_{str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))}.csv'

if default_dev == None:
    print('No avaliable serial devices found: Exiting SHIFU')
    sys.exit()

PORT = input_with_preset("Enter port name: ", f'{default_dev}')
BAUD = input_with_preset("Enter baud rate: ", f'{default_baud}')
filename = input_with_preset("Enter log file name: ", f'{default_name}')

# Pressure transducer mapping
Amax = 20e-3
Amin = 4e-3
# Setting calibrating resistor values for PT0 - PT7
R = [220.0, 220.0, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan]
# Setting pressure ranges on PT0 - PT7
Pmax = [250.0, 40.0, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan]
Pmin = [0.0, 0.0, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan]

Vmax = [Amax * r for r in R]
Vmin = [Amin * r for r in R]

rollingSample = 100

rollingP = [deque(maxlen=rollingSample) for _ in range(8)]
P_avg = [0.0] * 8

ser = serial.Serial(PORT, BAUD, timeout = 1)
print(f'Listening on {PORT}')

try:
    line = ser.readline().decode('utf-8').strip()   
    print(line)

    ser.write((input() + "\n").encode("utf-8"))
    ser.flush()
    with open(filename, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        headers = (["timestamp", "elapsed(s)"] + [f"PT{i}" for i in range(8)] + [f"TC{i}" for i in range(4)])
        csv_writer.writerow(headers)
        csv_file.flush()

        print(f"Logging started. Writing directly to {filename}")

        while True:

            if ser.in_waiting > 0: 
                decoded_line = ser.readline().decode('utf_8').strip()
                if decoded_line:
                    try:
                        data_fields = decoded_line.split(',')

                        if len(data_fields) >= 13:

                            if len(data_fields) >= 9:
                                relTime = int(data_fields[0])
                                seconds = relTime / 1000

                                ptVal = [int(val) for val in data_fields[1:9]]
                                volt = [float(val) * 5.0 / 1023.0 for val in ptVal]
                                pressure = [Pmin + (v - Vmin) * ((Pmax - Pmin) / (Vmax - Vmin)) for v, Vmin, Vmax, Pmin, Pmax in zip(volt, Vmin, Vmax, Pmin, Pmax)]
                                
                                for i in range(8):

                                    rollingP[i].append(pressure[i])
                                    P_avg[i] = sum(rollingP[i]) / len(rollingP[i])

                            tcVal = [float(val) for val in data_fields[9:13]]
                            temperature = tcVal

                            cal_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

                            row = [cal_time, seconds] + pressure + temperature
                            csv_writer.writerow(row)
                            csv_file.flush()

                            pt_string = " | ".join(f"PT{i}: {p:.1f}" for i, p in enumerate(P_avg))
                            tc_string = " | ".join(f"TC{i}: {t:.1f}°C" for i, t in enumerate(temperature))

                            # dashboard = (
                                # f"\033[4A\r\033[K" + "-" * 80 + "\n"
                                # f"\r\033[K{seconds:.2f}s | {pt_string}\n"
                                # f"\r\033[K{tc_string}\n"
                                # "\r\033[K" + "-" * 80
                            # )

                            dashboard = (
                                f"\033[H"                            # Move cursor to top-left
                                f"SHIFU TELEMETRY SYSTEM\033[K\n"  
                                f"{'-' * 80}\033[K\n"                
                                f"Time:     | {seconds:.2f}s\033[K\n"
                                f"Pressure: | {pt_string}\033[K\n"
                                f"Temp:     | {tc_string}\033[K\n"    # Starts cleanly on the left margin
                                f"{'-' * 80}\033[K\n"        
                                f"\033[J"                            # Clear any stray code below
                            )

                            print(dashboard, end="", flush=True)

                    except (ValueError, IndexError, UnicodeDecodeError):
                        continue

except KeyboardInterrupt:
    print("\nStopping...")
    ser.write
finally:
    hard_reset_mega(ser)
    ser.close()