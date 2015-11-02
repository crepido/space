# -*- coding: latin-1 -*-
__author__ = 'tobias'

import serial
import time


def send_command(com):
    ser.write(com+"\r\n")
    time.sleep(2)
    ret = []
    while ser.inWaiting() > 0:
        msg = ser.readline().strip()
        msg = msg.replace("\r", "")
        msg = msg.replace("\n", "")
        if msg != "":
            ret.append(msg)
    return ret


def convert(string):
    d = int(string[:2])
    m = float(string[2:])
    return float(d+m/60)


def conv(pos):
    str = pos[1].split(",")
    print(str)

    lat = str[1]
    lon = str[2]
    alt = str[3]
    speed = str[7]
    course = str[8]


    lon_d = convert(lon)
    lat_d = convert(lat)

    print("LON:", lon_d)
    print("LAT:", lat_d)
    print("ALT: "+alt)
    print("SPEED: "+speed)
    print("COURSE: "+course)

    a = float(12.303)
    print("hshhd %.9f" % a)

    url = "http://maps.google.com/maps?z=12&t=m&q=loc:%.9f+%.9f" % (lon_d, lat_d)
    print(url)


# ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, bytesize=8, parity='N', stopbits=1)
ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, timeout = 1)
ser.close()
ser.open()
print("isOpen:"+str(ser.isOpen()))
print("open serial")

print(send_command("AT"))

# GPS 
gps = send_command("AT+CGPSINF=0")
print("GPS:")
print(gps)

conv(gps)

# Signal quality
q = send_command("AT+CSQ")
print("Signal:")
print(q)

print(send_command("AT+COPN?"))
print(send_command("AT+CPIN?"))
print(send_command("AT+GSN"))


ser.close()

