__author__ = 'tobias'

import threading
import time
import Queue
import os

from sim908 import Sim908


class ComDevice(threading.Thread):

    def __init__(self,  q_com_device_in, q_com_device_out):
        super(ComDevice, self).__init__()

        self.sim = Sim908(True)
        self.q_com_device_in = q_com_device_in
        self.q_com_device_out = q_com_device_out
        self.mode = "Mode 1"
        self.running = True

    def send_images(self):
        list = os.listdir("data/send")
        if len(list) > 0:
            for item in list:
                print("Processing " + item)
                os.remove("data/send/" + item)

    def check_incoming_sms(self):
        msg = self.sim.read_one_sms().upper()
        if msg == "START" \
                or msg == "MODE 1" \
                or msg == "MODE 2" \
                or msg == "MODE 3" \
                or msg == "MODE 4" \
                or msg == "MODE 5" \
                or msg == "EXIT":
            self.q_com_device_out.put(msg)
        elif msg == "IP":
            None

    def check_incoming_queue(self):
        try:
            msg = self.q_mode.get_nowait().upper()
            if msg == "MODE 1" \
                    or msg == "MODE 2" \
                    or msg == "MODE 3" \
                    or msg == "MODE 4" \
                    or msg == "MODE 5" \
                    or msg == "START":

                print("Com: "+msg)
                self.mode = msg
            elif msg == "STOP" or msg == "EXIT":
                print("Com: Got exit")
                self.running = False

        except Queue.Empty:
            None

    def run(self):
        print("Starting ComDevice")

        i = 0
        while self.running:
            self.check_incoming_queue()
            self.check_incoming_sms()

            position = self.sim.get_gps_position()
            self.send_gps_position(position)

            time.sleep(10)

            i += 10

            if i == 100:
                # Mode 3, Ballong har brustit och vi faller
                self.q_com_device_out.put("Mode 3")

            if i == 200:
                # Mode 4, GPRS Online, Faller vidare
                self.q_com_device_out.put("Mode 4")

            if i == 300:
                # Mode 5, Vi har landat
                self.q_com_device_out.put("Mode 5")

            if self.mode == "Mode 1" or self.mode == "Mode 4":
                self.send_images()

        print("Stopping ComDevice")

    def send_gps_position(self, position):
        print("Sending gps position...")
        print("Latitude: %f" % position.get_latitude())
        print("Longitude: %f" % position.get_longitude())
