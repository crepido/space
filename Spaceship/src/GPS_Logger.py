__author__ = 'tobias'

import threading
import time
import Queue
import os

from sim908 import Sim908


class ComDevice(threading.Thread):

    def __init__(self,  q_com_device_in, q_com_device_out):
        super(ComDevice, self).__init__()

        self.sim = Sim908()
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

    def run(self):
        print("Starting GPS Logger")

        i = 0
        while self.running:
            try:
                # print("gps...")
                msg = self.q_com_device_in.get_nowait()
                if msg == "Mode 1":
                    self.mode = msg
                    print("Mode 1")
                elif msg == "Mode 2":
                    self.mode = msg
                    print("Mode 2")
                elif msg == "Mode 3":
                    self.mode = msg
                    print("Mode 3")
                elif msg == "Mode 4":
                    self.mode = msg
                    print("Mode 4")
                elif msg == "EXIT":
                    print("Got exit")
                    self.running = False
            except Queue.Empty:
                None

            time.sleep(1)

            i += 1

            if i == 250:
                # Mode 3, Ballong har brustit och vi faller
                self.q_com_device_out.put("Mode 3")

            if i == 400:
                # Mode 4, GPRS Online, Faller vidare
                self.q_com_device_out.put("Mode 4")

            if i == 500:
                # Mode 5, Vi har landat
                self.q_com_device_out.put("Mode 5")

            if self.mode == "Mode 1" or self.mode == "Mode 4":
                self.send_images()

        print("Stopping GPS Logger")

