__author__ = 'tobias'

from Camera import Camera
from GPS_Logger import ComDevice

import time
import Queue


class Space:
    def __init__(self):
        self.q_mode_camera = Queue.Queue()
        self.q_mode_com_device = Queue.Queue()
        self.q_com_device_out = Queue.Queue()

        self.camera = Camera(self.q_mode_camera)
        self.gps_logger = ComDevice(self.q_mode_com_device, self.q_com_device_out)
        self.running = True

    def set_mode(self, mode):
        print("Setting mode "+mode)
        self.q_mode_camera.put(mode)
        self.q_mode_com_device.put(mode)

    def shutdown(self):
        self.running = False
        self.set_mode("EXIT")
        print("All shut down")

    def run(self):

        self.gps_logger.start()
        self.camera.start()

        try:
            self.set_mode("Mode 1")
            time.sleep(100)
            self.set_mode("Mode 2")

            while self.running:
                try:
                    msg = self.q_com_device_out.get_nowait()
                    if msg == "Mode 3":
                        self.set_mode("Mode 3")
                    if msg == "Mode 4":
                        self.set_mode("Mode 4")
                    if msg == "Mode 5":
                        self.set_mode("Mode 5")
                except Queue.Empty:
                    None

                time.sleep(1)

        except KeyboardInterrupt:
            self.shutdown()


space = Space()
space.run()

print("SSS")
