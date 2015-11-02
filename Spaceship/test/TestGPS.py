__author__ = 'tobias'

from src import sim908

sim = sim908.Sim908()
location = sim.get_gps_location()
print(location.get_latitude())
print(location.get_longitude())
