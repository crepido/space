# -*- coding: latin-1 -*-
__author__ = 'tobias'

import serial
import time

def conversion(old):
    direction = {'N':-1, 'S':1, 'E': -1, 'W':1}
    new = old.replace(u'°',' ').replace('\'',' ').replace('"',' ')
    new = new.split()
    new_dir = new.pop()
    new.extend([0,0,0])
    return (int(new[0])+int(new[1])/60.0+int(new[2])/3600.0) * direction[new_dir]

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

def c(str):
	d = int(str[:2])
        m = float(str[2:])
        return d+m/60

def conv(pos):
        str = pos[1].split(",")
        print(str)

        lat = str[1]
        lon = str[2]
	alt = str[3]
	speed = str[7]
	course = str[8]

	print(c(lon))
	print(c(lat))
	print("ALT: "+alt)
	print("SPEED: "+speed)
	print("COURSE: "+course)
	


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

conv(gps)

# Signal quality
q = sendCommand("AT+CSQ")
print("Signal:")
print(q)

print(sendCommand("AT+COPN?"))
print(sendCommand("AT+CPIN?"))
print(sendCommand("AT+GSN"))


ser.close()

