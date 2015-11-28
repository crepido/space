# coding=latin-1
__author__ = 'tobias'

import threading
import time
import Queue
import os
import subprocess
import logging
import urllib

from sim908 import Sim908


class ComDevice(threading.Thread):

    def __init__(self,  q_com_device_in, q_com_device_out):
        super(ComDevice, self).__init__()

        self.sim = Sim908()
        self.q_com_device_in = q_com_device_in
        self.q_com_device_out = q_com_device_out
        self.mode = "Mode 0"
        self.running = True
        self.max_altitude = 0

        self.online = False

        self.sim.start_gps()
        self.sim.start_http()

        self.names = {"+46733770119": "Tobias"}

    def send_images(self):
        list = os.listdir("data/send")
        if len(list) > 0:
            for item in list:
                logging.info("Processing " + item)
               
                signal = self.sim.get_signal_level2()
                
                with open("data/send/"+item, "rb") as f:
                    data = f.read()
                    encoded = data.encode("base64")
                    #encoded2 = urllib.urlencode({"b": encoded})

                try:
                    if signal > 10:
                        self.sim.send_command("AT+HTTPPARA=\"URL\",\"http://spaceshiptracker.glenngbg.c9users.io/api/images?"+encoded+"\"")
                        self.sim.send_command_contains("AT+HTTPACTION=1", ["+HTTPACTION:"])
                        self.sim.send_command("AT")
                        time.sleep(0.5)
                        logging.info("Skickat bild")
                    else:
                        logging.debug("Signal is low, do not send images")
                   
                except RuntimeError:
                    logging.exception("Failed to send commands.")
                    self.sim.start_http()
                finally:
                    pass     
                
                os.remove("data/send/" + item)

    def find_words(self, cmd, expected_words):
        for word in expected_words:
            if cmd.find(word) == -1:
                return False
        return True

    def get_sender(self, sms):
        sender = str(sms[0]).replace("\"", "")
        name = ""
        logging.info("msisdn: " + sender)
        if sender == "+46733770119":
            name = "Tobias"
        if sender == "+46735581533":
            name = "Fredrik"
        if sender == "+46709200291":
            name = "Lotta"
        return name

    def check_incoming_sms(self):
        try:
            sms = self.sim.read_one_sms()
            if sms is not None:
                cmd = sms[1].upper()
                logging.info("Received SMS "+cmd)

                if cmd == "START" \
                        or cmd == "MODE 1" \
                        or cmd == "MODE 2" \
                        or cmd == "MODE 3" \
                        or cmd == "EXIT":
                    self.q_com_device_out.put(cmd)
                    self.sim.send_sms(sms[0], "OK")
                elif cmd == "IP":
                    res = subprocess.check_output("ifconfig | grep eth0 -A 2 | grep \"inet addr\"", shell=True)
                    self.sim.send_sms(sms[0], res)
                elif cmd == "POS":
                    position = self.sim.get_gps_position()
                    msg = str(position.get_longitude()) + " " + str(position.get_latitude())
                    self.sim.send_sms(sms[0], msg)
                elif cmd == "SHUTDOWN":
                    os.system("shutdown -h now")
                    self.sim.send_sms(sms[0], "System shutdown initiated")
                elif self.find_words(cmd, {"HETER", "DU"}):
                    self.sim.send_sms(sms[0], "Jag heter CrepidoInSpace!")

                elif self.find_words(cmd, {"VAR"}):
                    position = self.sim.get_gps_position()
                    msg = str(position.get_longitude()) + " " + str(position.get_latitude())
                    self.sim.send_sms(sms[0], "Jag är i rymden. Min position är "+msg+". Min höjd är "+
                                      str(position.get_altitude()) + " meter")

                elif self.find_words(cmd, {"CHEF"}):
                    self.sim.send_sms(sms[0], "Min chef är Lotta Sundqvist")

                elif self.find_words(cmd, {"VEM", "JAG"}):
                    name = self.get_sender(sms)

                    if name != "":
                        self.sim.send_sms(sms[0], "Du är "+name)
                    else:
                        self.sim.send_sms(sms[0], "Jag vet inte vem du är. Skicka ditt namn med sms: Jag heter Kalle")

                elif self.find_words(cmd, {"JAG", "HETER"}):
                    sender = str(sms[0])

                    tmp = cmd
                    name = tmp.replace("JAG HETER ").trim()
                    self.name[sender] = name

                    self.sim.send_sms(sms[0], "Hej "+name)

                elif self.find_words(cmd, {"VARMT"}) or self.find_words(cmd, {"TEMPERATUR"}):
                    self.sim.send_sms(sms[0], "Just nu är det 21 grader i skeppet.")

                elif self.find_words(cmd, {"LEDORD"}) or self.find_words(cmd, {"Värdegrund"}):
                    self.sim.send_sms(sms[0], "Våga säga nej. Sök alltid ett ja. Fastna aldrig i nja.")

                elif self.find_words(cmd, {"HEJ"}):
                    name = self.get_sender(sms)

                    if name != "":
                        self.sim.send_sms(sms[0], "Hej "+name+"!")
                    else:
                        self.sim.send_sms(sms[0], "Hej!")

                elif self.find_words(cmd, {"LOTTA"}):
                    self.sim.send_sms(sms[0], "Wow!")

                elif self.find_words(cmd, {"CREPIDO"}):
                    self.sim.send_sms(sms[0], "Crepido är ett konsultbolag som tillför innovation och energi till våra "
                                              "kunder.")
                else:
                    self.sim.send_sms(sms[0], "Jag förstår inte.")
        except RuntimeError:
            logging.exception("Failed to read incoming sms or queue")
        finally:
            pass

    def change_mode(self, msg):
        logging.debug("Com: " + msg)
        self.mode = msg

    def check_incoming_queue(self):
        try:
            msg = self.q_com_device_in.get_nowait().upper()
            if msg == "MODE 1" \
                    or msg == "MODE 2" \
                    or msg == "MODE 3" \
                    or msg == "START":
                self.change_mode(msg)
            elif msg == "STOP" or msg == "EXIT":
                logging.info("Com: Got exit")
                self.running = False

        except Queue.Empty:
            None
        finally:
            pass

    def check_online(self):
        online = self.sim.is_online()
        if self.online != online:
            self.online = online
            self.online_action()

    # Ensure 50 meters drop for each 10 sec measure
    def is_falling(self, altitude):
        falling = True
        last = self.max_altitude
        for item in altitude:
            logging.debug(item)
            if item >= last - 50:
                falling = False
            last = item
        return falling and len(altitude) == 6

    def run(self):
        logging.info("Starting ComDevice")

        i = 0
        altitude = []
        while self.running:
            self.check_incoming_queue()

            if i % 2 == 0:
                self.check_incoming_sms()

            # Each 10 sec
            if i % 10 == 0:
                self.check_online()
                position = self.sim.get_gps_position()

                # Save max altitude
                if position.get_altitude() > self.max_altitude:
                    self.max_altitude = position.get_altitude()

                altitude.insert(0, position.get_altitude())
                if len(altitude) > 6:
                    altitude.pop()

                if self.mode == "MODE 1" and self.is_falling(altitude):
                    self.q_com_device_out.put("MODE 2")

                    # if self.mode == "MODE 2" and self.has_landed(altitude):
                    # Check if landed

                if self.mode == "MODE 1" or self.mode == "MODE 2":
                    self.send_gps_position(position)

                # Each minute
                if self.mode == "MODE 3" and i == 0:
                    self.send_gps_position(position)

                    #if self.online:
                    #    self.send_images()

            time.sleep(1)
            i += 1
            if i >= 60:
                i = 0

        logging.info("Stopping ComDevice")

    def online_action(self):
        logging.info("Now online: "+str(self.online))
        if self.online:
            self.q_com_device_out.put("ONLINE")
        else:
            self.q_com_device_out.put("OFFLINE")

    def send_gps_position(self, position):
        logging.info("Latitude: %f" % position.get_latitude())
        logging.info("Longitude: %f" % position.get_longitude())
        logging.info("Altitude: %f" % position.get_altitude())

        str_lat = str(position.get_latitude())
        str_lon = str(position.get_longitude())
        str_alt = str(position.get_altitude())

        try:
            if position.get_latitude() == 0.0:
                logging.info("Ingen position")
            elif self.online:
                self.sim.send_command("AT+HTTPPARA=\"URL\",\"http://spaceshiptracker.glenngbg.c9users.io/api/positions?lat="+str_lat+"&lon="+str_lon+"&alt="+str_alt+"&ship=Ballon\"")
                self.sim.send_command_contains("AT+HTTPACTION=1", ["+HTTPACTION:"])
                self.sim.send_command("AT")
                time.sleep(0.5)
                logging.info("Skickat gps")
            else:
                logging.info("Offline, skickar inte gps")
        except RuntimeError:
            logging.exception("Failed to send commands.")
            self.sim.start_http()
        finally:
            pass