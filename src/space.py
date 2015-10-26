__author__ = 'tobias'

from Queue import Queue
from sim908 import Sim908
from Camera import Camera
from GPS_Logger import GPS_Logger

class Space:
    def __init__(self):
        self.q = Queue()
        self.sim = Sim908()
        self.camera = Camera()
        self.gps_logger = GPS_Logger(self.sim)

    def run(self):
        while True:




space = Space()
space.run()

