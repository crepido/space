__author__ = 'tobias'

import threading
import time
import Queue

from sim908 import Sim908


class ComDevice(threading.Thread):

    def __init__(self,  q_mode, q_fall):
        super(ComDevice, self).__init__()

        self.sim = Sim908()
        self.q_mode = q_mode
        self.q_fall = q_fall
        self.running = True

    def run(self):
        print("Starting GPS Logger")

        i = 0
        while self.running:
            try:
                # print("gps...")
                msg = self.q_mode.get_nowait()
                if msg == "Mode 1":
                    print("Mode 1")
                elif msg == "Mode 2":
                    print("Mode 2")
                elif msg == "Mode 3":
                    print("Mode 3")
                elif msg == "Mode 4":
                    print("Mode 4")
                elif msg == "EXIT":
                    print("Got exit")
                    self.running = False
            except Queue.Empty:
                None

            time.sleep(1)

            i += 1

            if i == 250:
                self.q_fall.put("FALLING")

            if i == 400:
                self.q_fall.put("ONLINE")

            if i == 500:
                self.q_fall.put("LANDED")

        print("Stopping GPS Logger")

