__author__ = 'tobias'

import RPi.GPIO as GPIO
import time
import threading

class Camera(threading.Thread):
    def __init__(self, q):
        self.q = q
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(7, GPIO.OUT)
        p = GPIO.PWM(7, 50)
        p.start(7.5)

        self.mode = 1

        threading.Thread.__init__(self)
        self._running = True

    def run(self):
        print "Starting Camera"

        msg = self.q.get()

        if msg == "MODE 1":
            self.run_mode_1()

        while self._running:
            time.sleep(10)

    def run_mode_1(self):
        None


