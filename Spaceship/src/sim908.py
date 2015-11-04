__author__ = 'tobias'

import time
import serial


class Position:
    def __init__(self, gps_data_str):
        gps_data_list = gps_data_str[1].split(",")
        print(gps_data_list)

        lat = gps_data_list[1]
        lon = gps_data_list[2]

        self.longitude = Position.convert(lon)
        self.latitude = Position.convert(lat)
        self.altitude = gps_data_list[3]
        self.speed = gps_data_list[7]
        self.course = gps_data_list[8]

    @staticmethod
    def convert(string):
        if string == "0.000000":
            return 0.0

        d = int(string[:2])
        m = float(string[2:])
        return float(d+m/60)

    def get_latitude(self):
        return self.latitude

    def get_longitude(self):
        return self.longitude

    def get_altitude(self):
        return self.altitude

    def get_speed(self):
        return self.speed

    def get_course(self):
        return self.course

    def get_maps_url(self):
        return "http://maps.google.com/maps?z=12&t=m&q=loc:%.9f+%.9f" % (self.longitude, self.latitude)


class Sim908:

    def __init__(self):
        self.ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, timeout=1)
        self.ser.close()
        self.ser.open()

        self.send_command("AT+CGPSPWR=1")
        self.send_command("AT+CGPSRST=1")
        self.send_command("AT")
        time.sleep(10)

    def get_gps_position(self):
        gps = self.send_command("AT+CGPSINF=0")
        pos = Position(gps)
        return pos

    def gps_power_on(self):
        self.send_command("AT+CGPSPWR=1")

    def gps_reset(self):
        self.send_command("AT+CGPSRST=1")

    def get_signal_level(self):
        result = self.send_command("AT+CSQ")
        return result[1]

    def send_sms(self, number, text):
        self.send_command_with_result("AT", "OK")
        self.send_command("AT+CSCA?")
        self.send_command("AT+CMGF=1")  # Set sms message format
        self.send_command_with_result("AT+CMGS=\""+number+"\"", ">")  # Set sms message format
        self.send_command(text)
        self.send_command("\x1A")  # TODO Must send as HEX... This may not work yet...

    def read_one_sms(self):
        # Read
        print(self.send_command("AT+CMGR=1"))
        # Delete
        print(self.send_command("AT+CMGD=1"))

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

    def send_command_with_result(self, command, expected_result):
        result = self.send_command(command)
        if result[1] != expected_result:
            raise RuntimeError("Error in command response")
        return True