__author__ = 'tobias'

import serial

ser = serial.Serial(port='/tty/ttyAMA0', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1, xonoff=False, rtscts=False, dsrdtr=False)
cmd = "AT\r"
ser.write(cmd.encode())
msg = ser.read(64)
print(msg)