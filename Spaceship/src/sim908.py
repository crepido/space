__author__ = 'tobias'

import time
import serial
import logging


class Position:
    def __init__(self, gps_data_str):
        gps_data_list = gps_data_str[1].split(",")
        logging.debug(gps_data_list)
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

    def __init__(self, debug):
        logging.debug("init Sim908")
        self.debug = debug
        self.ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, timeout=1)
        self.ser.close()
        self.ser.open()
        self.start_gps()

    def start_gps(self):
        self.send_command("AT+CGPSPWR=1")
        self.send_command("AT+CGPSRST=1")
        self.send_command("AT")

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
        self.send_command("AT+CMGS=\""+str(number)+"\"", [">"])  # Set sms message format
        self.send_command(text, [">"])
        self.send_command("\x1A")
        self.send_command("AT")

    def read_one_sms(self):
        sms_list = self.send_command("AT+CMGL=\"ALL\"")
        for x in range(0, len(sms_list)):
            if sms_list[x].startswith("+CMGL:"):
                ctr = sms_list[x]
                msg = sms_list[x+1]

                if self.debug:
                    logging.debug("SMS "+str(x)+":"+msg)

                index = int(sms_list[x].split(",")[0].split(":")[1])
                # Delete
                self.send_command("AT+CMGD="+str(index))

                msisdn = str(ctr.split(",")[2].replace("\"", ""))
                logging.debug("MSISDN: " + msisdn)
                return [msisdn, msg]

    def send_command(self, com, expected_result=["OK", "ERROR"]):
        response = False
        self.ser.write(com+"\r\n")
        ret = []
        i = 0
        while not response:
            msg = self.ser.readline().strip()
            msg = msg.replace("\r", "")
            msg = msg.replace("\n", "")
            if msg != "":
                ret.append(msg)

            if self.is_done(msg, expected_result):
                response = True

            i += 1
            if i > 10:
                logging(ret)
                raise RuntimeError("Expected result")

        logging.debug(ret)

        return ret

    def send_command_contains(self, com, expected_result=["OK", "ERROR"]):
        response = False
        self.ser.write(com+"\r\n")
        ret = []
        i = 0
        while not response:
            msg = self.ser.readline().strip()
            msg = msg.replace("\r", "")
            msg = msg.replace("\n", "")
            if msg != "":
                ret.append(msg)

            if self.is_done_contains(msg, expected_result):
                response = True

            i += 1
            if i > 10:
                logging.error(ret)
                raise RuntimeError("Expected result")

        logging.debug(ret)

        return ret

    def is_done(self, msg, expected_result):
        for res in expected_result:
            if msg == res:
                return True
        return False

    def is_done_contains(self, msg, expected_result):
        for res in expected_result:
            if msg.find(res) > -1:
                return True
        return False

    def send_command_with_result(self, command, expected_result):
        result = self.send_command(command)
        if result[1] != expected_result:
            raise RuntimeError("Error in command response")
        return True

    def is_online(self):
        res = self.send_command("AT+CSQ")
        signal = int(res[1].split(":")[1].split(",")[0])

        logging.debug("Signal level: "+str(signal))
        if signal == 99:
            logging.debug("no connection")
            return False
        if signal > 10:
            logging.debug(">10")

        return True