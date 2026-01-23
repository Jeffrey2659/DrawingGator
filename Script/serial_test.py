#!/usr/bin/env python3
"""
Stream g-code to a GRBL/GRBL-Polar controller with a simple buffer tracker.
"""

import serial
import time
import argparse

RX_BUFFER_SIZE = 128  # GRBL's default serial RX size

parser = argparse.ArgumentParser(
    description='Stream g-code file to GRBL. (Requires pyserial)'
)
parser.add_argument('gcode_file', type=argparse.FileType('r'),
                    help='g-code filename to be streamed')
parser.add_argument('device_file', help='serial device path (e.g. COM3 or /dev/ttyUSB0)')
parser.add_argument('-q', '--quiet', action='store_true', default=False,
                    help='suppress per-line logs')
parser.add_argument('-s', '--settings', action='store_true', default=False,
                    help='settings write mode (simple call/response)')
args = parser.parse_args()

ser = serial.Serial(args.device_file, 115200, timeout=1)
f = args.gcode_file
verbose = not args.quiet
settings_mode = args.settings

# Wake up GRBL
print("Initializing GRBL...")
ser.write(b"\r\n\r\n")
time.sleep(2)
ser.reset_input_buffer()  # flush startup text

l_count = 0

if settings_mode:
    # Simple call/response for settings lines
    print(f"SETTINGS MODE: Streaming {args.gcode_file.name} to {args.device_file}")
    for line in f:
        l_count += 1
        l_block = line.strip()
        if not l_block:
            continue
        if verbose:
            print(f"SND: {l_count}: {l_block}")
        ser.write((l_block + '\n').encode('ascii', 'ignore'))
        grbl_out = ser.readline().decode(errors='ignore').strip()
        if verbose:
            print("REC:", grbl_out)
else:
    # Aggressive streaming with simple RX buffer tracking
    g_count = 0
    c_line = []
    for line in f:
        l_count += 1
        l_block = line.strip()
        if not l_block:
            continue

        # Track how many chars we’ve pushed into GRBL’s RX buffer (add 1 for newline)
        c_line.append(len(l_block) + 1)

        grbl_out = ''
        # IMPORTANT: use logical OR, and pyserial 3.x's in_waiting property
        while sum(c_line) >= (RX_BUFFER_SIZE - 1) or ser.in_waiting:
            out_temp = ser.readline().decode(errors='ignore').strip()
            if not out_temp:
                break
            if ('ok' not in out_temp) and ('error' not in out_temp):
                # non-final responses (e.g., status/debug); show if not quiet
                if verbose:
                    print("  Debug:", out_temp)
            else:
                g_count += 1
                grbl_out += f"{out_temp}#{g_count} "
                if c_line:
                    del c_line[0]

        if verbose:
            print(f"SND: {l_count}: {l_block}", end=' ')
        ser.write((l_block + '\n').encode('ascii', 'ignore'))
        if verbose:
            print(f"BUF:{sum(c_line)} REC:{grbl_out}")

print("\nG-code streaming finished!")
print("WARNING: Let GRBL finish its buffered blocks before disconnecting.")
input("Press <Enter> to close the port... ")

f.close()
ser.close()
