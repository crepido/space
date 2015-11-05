__author__ = 'tobias'

import src.sim908
import time

sim = src.sim908.Sim908(True)
time.sleep(10)

while True:
    position = sim.get_gps_position()
    print(position.get_latitude())
    print(position.get_longitude())
    time.sleep(10)