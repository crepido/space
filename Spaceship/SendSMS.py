__author__ = 'tobias'

import src.sim908
import time


sim = src.sim908.Sim908(True)

#position = sim.get_gps_position()
#print(position.get_latitude())
#print(position.get_longitude())

#sim.reset()

# Glenn
sim.send_sms("+46704173699", "SMS from Spacecraft")

#sim.send_sms('+46733770119', "test")


print("done")
