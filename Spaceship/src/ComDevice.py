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

        self.sim = Sim908(True)
        self.q_com_device_in = q_com_device_in
        self.q_com_device_out = q_com_device_out
        self.mode = "Mode 1"
        self.running = True
        self.max_altitude = 0

        self.online = False

        try:
            self.sim.send_command("AT+CGATT?")
            self.sim.send_command("AT+CGATT=1")
            self.sim.send_command("AT+SAPBR=3,1,\"CONTYPE\",\"GPRS\"")
            self.sim.send_command("AT+SAPBR=3,1,\"APN\",\"online.telia.se\"")
            self.sim.send_command("AT+SAPBR=1,1")
            self.sim.send_command("AT+HTTPINIT")
        except RuntimeError:
            logging.error("Failed to init ComDevice")

    def send_images(self):
        list = os.listdir("data/send")
        if len(list) > 0:
            for item in list:
                logging.info("Processing " + item)
                os.remove("data/send/" + item)

    def check_incoming_sms(self):
        sms = self.sim.read_one_sms()
        if sms is not None:
            cmd = sms[1].upper()

            if cmd == "START" \
                    or cmd == "MODE 1" \
                    or cmd == "MODE 2" \
                    or cmd == "MODE 3" \
                    or cmd == "MODE 4" \
                    or cmd == "MODE 5" \
                    or cmd == "EXIT":
                self.q_com_device_out.put(cmd)
            elif cmd == "IP":
                res = subprocess.check_output("ifconfig | grep eth0 -A 2 | grep \"inet addr\"", shell=True)
                self.sim.send_sms(sms[0], res)
            elif cmd == "POS":
                position = self.sim.get_gps_position()
                msg = str(position.get_longitude()) + " " + str(position.get_latitude())
                self.sim.send_sms(sms[0], msg)

    def change_mode(self, msg):
        logging.debug("Com: " + msg)
        self.mode = msg

    def check_incoming_queue(self):
        try:
            msg = self.q_com_device_in.get_nowait().upper()
            if msg == "MODE 1" \
                    or msg == "MODE 2" \
                    or msg == "MODE 3" \
                    or msg == "MODE 4" \
                    or msg == "MODE 5" \
                    or msg == "START":
                self.change_mode(msg)
            elif msg == "STOP" or msg == "EXIT":
                logging.info("Com: Got exit")
                self.running = False

        except Queue.Empty:
            None

    def check_online(self):
        if not self.online and self.sim.is_online():
            self.online = True
            self.online_action()
        if self.online and not self.sim.is_online():
            self.online = False
            self.online_action()

    def run(self):
        logging.info("Starting ComDevice")

        i = 0
        while self.running:
            try:
                self.check_incoming_queue()
                self.check_incoming_sms()
            except RuntimeError:
                logging.exception("Failed to read incoming sms or queue")

            if i == 0 and self.mode == "MODE 1" \
                    or self.mode == "MODE 2" \
                    or self.mode == "MODE 3" \
                    or self.mode == "MODE 4" \
                    or self.mode == "MODE 5":

                position = self.sim.get_gps_position()
                self.send_gps_position(position)

                # Save max altitude
                if position.get_altitude() > self.max_altitude:
                    self.max_altitude = position.get_altitude()

                if self.mode == "MODE 3":
                    altitude = position.get_altitude()

            self.check_online()

            time.sleep(1)

            i += 1

            if i > 10:
                i = 0

            # if i == 100:
            #     # Mode 3, Ballong har brustit och vi faller
            #     self.q_com_device_out.put("Mode 3")
            #
            # if i == 200:
            #     # Mode 4, GPRS Online, Faller vidare
            #     self.q_com_device_out.put("Mode 4")
            #
            # if i == 300:
            #     # Mode 5, Vi har landat
            #     self.q_com_device_out.put("Mode 5")

            if self.mode == "Mode 1" or self.mode == "Mode 4":
                self.send_images()

        logging.info("Stopping ComDevice")

    def online_action(self):
        logging.info("Now online: "+str(self.online))

    def send_gps_position(self, position):
        logging.info("Latitude: %f" % position.get_latitude())
        logging.info("Longitude: %f" % position.get_longitude())
        
        str_lat = str(position.get_latitude())
        str_lon = str(position.get_longitude())
        str_alt = str(position.get_altitude())

        try:
            self.sim.send_command("AT+HTTPPARA=\"URL\",\"http://spaceshiptracker.glenngbg.c9users.io/api/positions?lat="+str_lat+"&lon="+str_lon+"&alt="+str_alt+"&ship=Ballon\"")
            self.sim.send_command_contains("AT+HTTPACTION=1", ["+HTTPACTION:"])
        except RuntimeError:
            logging.exception("Failed to send commands.")

        logging.info("done")
