__author__ = 'tobias'

import src.sim908
import time


sim = src.sim908.Sim908()
time.sleep(1)

#position = sim.get_gps_position()
#print(position.get_latitude())
#print(position.get_longitude())

#sim.reset()
#sim.send_sms('+46733770119', "test")

sim.receive()

time.sleep(1)
print("done")