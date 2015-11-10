__author__ = 'tobias'

import threading
import time
import Queue
import os
import subprocess
import logging

from sim908 import Sim908


class ComDevice(threading.Thread):

    def __init__(self,  q_com_device_in, q_com_device_out):
        super(ComDevice, self).__init__()

        self.sim = Sim908()
        self.q_com_device_in = q_com_device_in
        self.q_com_device_out = q_com_device_out
        self.mode = "Mode 0"
        self.running = True
        self.max_altitude = 0

        self.online = False

        self.sim.start_gps()
        self.sim.start_http()

    def send_images(self):
        list = os.listdir("data/send")
        if len(list) > 0:
            for item in list:
                logging.info("Processing " + item)
                os.remove("data/send/" + item)

    def check_incoming_sms(self):
        try:
            sms = self.sim.read_one_sms()
            if sms is not None:
                cmd = sms[1].upper()
                logging.info("Received SMS "+cmd)

                if cmd == "START" \
                        or cmd == "MODE 1" \
                        or cmd == "MODE 2" \
                        or cmd == "MODE 3" \
                        or cmd == "EXIT":
                    self.q_com_device_out.put(cmd)
                    self.sim.send_sms(sms[0], "OK")
                elif cmd == "IP":
                    res = subprocess.check_output("ifconfig | grep eth0 -A 2 | grep \"inet addr\"", shell=True)
                    self.sim.send_sms(sms[0], res)
                elif cmd == "POS":
                    position = self.sim.get_gps_position()
                    msg = str(position.get_longitude()) + " " + str(position.get_latitude())
                    self.sim.send_sms(sms[0], msg)
                elif cmd == "SHUTDOWN":
                    os.system("shutdown -h now")
                    self.sim.send_sms(sms[0], "System shutdown initiated")
                else:
                    self.sim.send_sms(sms[0], "Error")
        except RuntimeError:
            logging.exception("Failed to read incoming sms or queue")
        finally:
            pass

    def change_mode(self, msg):
        logging.debug("Com: " + msg)
        self.mode = msg

    def check_incoming_queue(self):
        try:
            msg = self.q_com_device_in.get_nowait().upper()
            if msg == "MODE 1" \
                    or msg == "MODE 2" \
                    or msg == "MODE 3" \
                    or msg == "START":
                self.change_mode(msg)
            elif msg == "STOP" or msg == "EXIT":
                logging.info("Com: Got exit")
                self.running = False

        except Queue.Empty:
            None
        finally:
            pass

    def check_online(self):
        online = self.sim.is_online()
        if self.online != online:
            self.online = online
            self.online_action()

    def is_falling(self, altitude):
        falling = True
        last = self.max_altitude
        for item in altitude:
            logging.debug(item)
            if item >= last:
                falling = False
            last = item
        return falling and len(altitude) == 6

    def run(self):
        logging.info("Starting ComDevice")

        i = 0
        altitude = []
        while self.running:
            self.check_incoming_queue()

            # Each 10 sec
            if i % 10 == 0:
                self.check_incoming_sms()
                self.check_online()
                position = self.sim.get_gps_position()

                # Save max altitude
                if position.get_altitude() > self.max_altitude:
                    self.max_altitude = position.get_altitude()

                altitude.insert(0, position.get_altitude())
                if len(altitude) > 6:
                    altitude.pop()

                if self.mode == "MODE 1" and self.is_falling(altitude):
                    self.q_com_device_out.put("MODE 2")

                # if self.mode == "MODE 2" and self.has_landed(altitude):
                    # Check if landed

                if self.mode == "MODE 1" or self.mode == "MODE 2":
                    self.send_gps_position(position)

                # Each minute
                if self.mode == "MODE 3" and i == 0:
                    self.send_gps_position(position)

                if self.online:
                    self.send_images()

            time.sleep(1)
            i += 1
            if i >= 60:
                i = 0

        logging.info("Stopping ComDevice")

    def online_action(self):
        logging.info("Now online: "+str(self.online))
        if self.online:
            self.q_com_device_out.put("ONLINE")
        else:
            self.q_com_device_out.put("OFFLINE")

    def send_gps_position(self, position):
        logging.info("Latitude: %f" % position.get_latitude())
        logging.info("Longitude: %f" % position.get_longitude())
        logging.info("Altitude: %f" % position.get_altitude())

        str_lat = str(position.get_latitude())
        str_lon = str(position.get_longitude())
        str_alt = str(position.get_altitude())

        try:
            if position.get_latitude() == 0.0:
                logging.info("Ingen position")
            elif self.online:
                self.sim.send_command("AT+HTTPPARA=\"URL\",\"http://spaceshiptracker.glenngbg.c9users.io/api/positions?lat="+str_lat+"&lon="+str_lon+"&alt="+str_alt+"&ship=Ballon\"")
                self.sim.send_command_contains("AT+HTTPACTION=1", ["+HTTPACTION:"])
                self.sim.send_command("AT")
                time.sleep(0.5)
                logging.info("Skickat gps")
            else:
                logging.info("Offline, skickar inte gps")
        except RuntimeError:
            logging.exception("Failed to send commands.")
            self.sim.start_http()
        finally:
            pass