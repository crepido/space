__author__ = 'tobias'

import time
import serial


class Sim908:

    def __init__(self):
        pass

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

    def send_command(self, cmd):
        pass