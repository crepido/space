__author__ = 'tobias'

import time
import serial


class Sim908:

    def __init__(self):
        self.ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, timeout=1)
        self.ser.close()
        self.ser.open()

        self.send_command("AT+CGPSPWR=1")
        self.send_command("AT+CGPSRST=1")

    def get_gps_location(self):
        return None

    def gps_power_on(self):
        self.send_command("AT+CGPSPWR=1")

    def gps_reset(self):
        self.send_command("AT+CGPSRST=1")

    def gps_get(self):
        self.send_command("AT+CGPSINF=32")

    def get_signal_level(self):
        self.send_command("AT+CSQ")
        return result

    def send_command(self, com):
        self.ser.write(com+"\r\n")
        time.sleep(2)
        ret = []
        while self.ser.inWaiting() > 0:
            msg = self.ser.readline().strip()
            msg = msg.replace("\r", "")
            msg = msg.replace("\n", "")
            if msg != "":
                ret.append(msg)
        return ret