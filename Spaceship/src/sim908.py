__author__ = 'tobias'

import time
import serial
import logging


class Position:

    def __init__(self, gps_data_str):
        if gps_data_str != "":
            try:
                gps_data_list = gps_data_str[1].split(",")
                logging.debug(gps_data_list)
                lat = gps_data_list[1]
                lon = gps_data_list[2]

                self.longitude = Position.convert(lon)
                self.latitude = Position.convert(lat)
                self.altitude = float(gps_data_list[3])
                self.speed = gps_data_list[7]
                self.course = gps_data_list[8]
            except Exception:
                for item in gps_data_str:
                    logging.error(item)
                logging.exception("Could not parse gps string data ")
                self.init_empty()
        else:
            self.init_empty()

    def init_empty(self):
        self.longitude = 0.0
        self.latitude = 0.0
        self.altitude = 0.0
        self.speed = 0.0
        self.course = 0.0

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
        logging.debug("init Sim908")
        self.ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, timeout=1)
        self.ser.close()
        self.ser.open()
        self.gps_init_count = 0

    def start_gps(self):
        try:
            self.send_command("AT+CGPSPWR=1")
            self.send_command("AT+CGPSRST=1")
            self.send_command("AT")
            self.gps_init_count += 1
            if self.gps_init_count > 5:
                self.gps_init_count = 0
            return True
        except RuntimeError:
            logging.exception("Failed to init gps")
            return False

    def start_http(self):
        try:
            self.send_command("AT+CGATT?")
            self.send_command("AT+CGATT=1")
            self.send_command("AT+SAPBR=3,1,\"CONTYPE\",\"GPRS\"")
            self.send_command("AT+SAPBR=3,1,\"APN\",\"online.telia.se\"")
            self.send_command("AT+SAPBR=1,1")
            self.send_command("AT+HTTPINIT")
            return True
        except RuntimeError:
            logging.error("Failed to init ComDevice")
            return False

    def get_gps_position(self):
        try:
            gps = self.send_command("AT+CGPSINF=0")
            pos = Position(gps)

            if pos.get_latitude() == 0.0 and self.gps_init_count == 0:
                self.start_gps()
            return pos
        except RuntimeError:
            logging.exception("Failed to get gps position")
            self.start_gps()
            return Position("")

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
                logging.error(ret)
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
        try:
            res = self.send_command("AT+CSQ")
            signal = int(res[1].split(":")[1].split(",")[0])

            logging.debug("Signal level: "+str(signal)+" (0-31)")
            if signal == 99 or signal <= 2:
                logging.debug("no connection")
                return False

            return True
        except (RuntimeError, IndexError, ValueError):
            logging.error("Failed to check online status")
            return False
        finally:
            pass

     def get_signal_level2(self):
        try:
            res = self.send_command("AT+CSQ")
            signal = int(res[1].split(":")[1].split(",")[0])
            return signal
        except (RuntimeError, IndexError, ValueError):
            logging.error("Failed to get signal level")
            return 0
        finally:
            pass
