__author__ = 'tobias'

import src.sim908
import time

sim = src.sim908.Sim908(True)

while True:
    sms = sim.read_one_sms()

    print("Avsändare: "+sms[0])
    print("SMS: "+sms[1])

    time.sleep(5)