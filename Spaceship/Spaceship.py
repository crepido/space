__author__ = 'tobias'

from src.Camera import Camera
from src.ComDevice import ComDevice

import time
import Queue
import logging
import RPi.GPIO as GPIO


class Spaceship:
    def __init__(self):
        logging.info("Starting Spaceship")
        self.q_mode_camera = Queue.Queue()
        self.q_com_device_in = Queue.Queue()
        self.q_com_device_out = Queue.Queue()

        GPIO.setmode(GPIO.BOARD)
        # init pin 7 for camera PWM
        GPIO.setup(7, GPIO.OUT)
        # Init pin 11 for diode
        GPIO.setup(11, GPIO.OUT)
        # Init pin 13 for relay for power to servo
        GPIO.setup(13, GPIO.OUT)

        self.mode = ""
        self.online = False
        self.camera = Camera(self.q_mode_camera)
        self.com_device = ComDevice(self.q_com_device_in, self.q_com_device_out)
        self.running = True

    # Main loop
    def run(self):

        logging.info('Started')
        self.com_device.start()
        self.camera.start()

        try:
            while self.running:
                self.check_queue()
                self.blink_diode()
                time.sleep(2)
        except KeyboardInterrupt:
            self.shutdown()
        finally:
            pass
        GPIO.cleanup()
        logging.info('Finished')

    def set_mode(self, mode):
        logging.info("Setting mode "+mode)
        self.q_mode_camera.put(mode)
        self.q_com_device_in.put(mode)

    def shutdown(self):
        print("Shutting down...")
        self.running = False
        self.set_mode("EXIT")
        logging.info("All shut down")
        logging.info("Shutdown Spaceship")

    def check_queue(self):
        try:
            msg = self.q_com_device_out.get_nowait().upper()
            if msg == "MODE 1" \
                    or msg == "MODE 2" \
                    or msg == "MODE 3" \
                    or msg == "ONLINE" \
                    or msg == "OFFLINE" \
                    or msg == "START":
                self.set_mode(msg)
            elif msg == "EXIT":
                self.shutdown()
            elif msg == "ONLINE":
                self.online = True
            elif msg == "OFFLINE":
                self.online = False
        except Queue.Empty:
            None
        finally:
            pass

    def blink_diode(self):
        if self.mode == "":
            GPIO.output(11, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(11, GPIO.LOW)
            time.sleep(0.5)
            self.blink_online_status()

        elif self.mode == "MODE 1":
            self.blink()
            time.sleep(0.5)
            self.blink_online_status()

        elif self.mode == "MODE 2":
            self.blink()
            self.blink()
            time.sleep(0.5)
            self.blink_online_status()

        elif self.mode == "MODE 3":
            self.blink()
            self.blink()
            self.blink()
            time.sleep(0.5)
            self.blink_online_status()

    def blink_online_status(self):
        if self.online:
            GPIO.output(11, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(11, GPIO.LOW)
        else:
            time.sleep(0.5)

    @staticmethod
    def blink():
        GPIO.output(11, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(11, GPIO.LOW)
        time.sleep(0.1)


if __name__ == '__main__':
    logging.basicConfig(filename='/home/pi/space.log', format='%(asctime)s %(levelname)s : %(name)s : %(message)s',
                        level=logging.DEBUG)
    space = Spaceship()
    space.run()