__author__ = 'tobias'

import src.sim908
import time

sim = src.sim908.Sim908(True)

while True:
    sim.read_one_sms()
    time.sleep(5)