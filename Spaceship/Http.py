__author__ = 'tobias'

import src.sim908
import time


sim = src.sim908.Sim908(True)
time.sleep(1)

sim.send_command("AT+CGATT?")
sim.send_command("AT+CGATT=1")
sim.send_command("AT+SAPBR=3,1,\"CONTYPE\",\"GPRS\"")
sim.send_command("AT+SAPBR=3,1,\"APN\",\"online.telia.se\"")
sim.send_command("AT+SAPBR=1,1")
sim.send_command("AT+HTTPINIT")
sim.send_command("AT+HTTPPARA=\"URL\",\"http://www.google.com\"")
sim.send_command("AT+HTTPACTION=0")
sim.send_command("AT+HTTPREAD")



print("done")