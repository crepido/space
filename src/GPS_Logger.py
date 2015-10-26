__author__ = 'tobias'

import threading
import time


class GPS_Logger(threading.Thread):

    def __init__(self, sim):
        super(GPS_Logger, self).__init__()
        self.sim = sim

    def run(self):
        time.sleep(10)

