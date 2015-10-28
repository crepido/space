__author__ = 'tobias'

import serial
import time

def sendCommand(com):
    ser.write(com+"\r\n")
    time.sleep(2)
    ret = []
    while ser.inWaiting() > 0:
        msg = ser.readline().strip()
        msg = msg.replace("\r","")
        msg = msg.replace("\n","")
        if msg!="":
            ret.append(msg)
    return ret

#ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, bytesize=8, parity='N', stopbits=1)
ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, timeout = 1)
ser.close()
ser.open()
print("isOpen:"+str(ser.isOpen()))
print("open serial")

print(sendCommand("AT"))

# GPS 
gps = sendCommand("AT+CGPSINF=0")
print("GPS:")
print(gps)

# Signal quality
q = sendCommand("AT+CSQ")
print("Signal:")
print(q)

ser.close()
