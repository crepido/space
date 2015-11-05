__author__ = 'tobias'

import RPi.GPIO as GPIO
import time
import threading
import Queue
import os


class Camera(threading.Thread):
    def __init__(self, q_mode):
        self.q_mode = q_mode
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(7, GPIO.OUT)
        self.pwm = GPIO.PWM(7, 50)
        self.pwm.start(7.5)
        self.camera_position = "horizontal"

        self.mode = 1
        self.i = 0
        self.sleep = 0

        threading.Thread.__init__(self)
        self._running = True

    def check_messages(self):
        try:
            msg = self.q_mode.get_nowait().upper()
            if msg == "MODE 1" \
                    or msg == "MODE 2" \
                    or msg == "MODE 3" \
                    or msg == "MODE 4" \
                    or msg == "MODE 5" \
                    or msg == "START":

                print("Cam: "+msg)
                self.change_mode(msg)
            elif msg == "STOP" or msg == "EXIT":
                print("Cam: Got exit")
                self._running = False

        except Queue.Empty:
            None

    def change_mode(self, msg):
        self.mode = msg

        if msg == "MODE 3":
            print("Falling")

    def run(self):
        print "Starting Camera"

        i = 0
        t1 = 0
        while self._running:

            if i == 0:
                t1 = time.time()

            self.check_messages()

            if self.mode == "MODE 1":
                self.run_mode_1(i)
            if self.mode == "MODE 2":
                self.run_mode_2(i)
            if self.mode == "MODE 3":
                self.run_mode_3(i)
            if self.mode == "MODE 4":
                self.run_mode_4(i)
            if self.mode == "MODE 5":
                self.run_mode_5(i)
            else:
                time.sleep(1)

            i += 1
            if i >= 60:
                i = 0
                t2 = time.time()
                t = t2 - t1
                print("time: "+str(t))

        print("Stopping camera")

    def run_mode_1(self, i):
        if i % 10 == 0:
            self.movie10s()
            filename = self.take_picture()
            if i == 0:
                self.send_picture(filename)

            if self.camera_position == "vertical":
                self.position_camera("horizontal")
            else:
                self.position_camera("vertical")
        else:
            None

    def run_mode_2(self, i):

        if i == 0:
            self.movie10s()
        elif i < 10:
            None
        elif i % 10 == 0:
            self.take_picture()
            if self.camera_position == "vertical":
                self.position_camera("horizontal")
            else:
                self.position_camera("vertical")
            time.sleep(1)
        else:
            time.sleep(1)

    def run_mode_3(self, i):
        time.sleep(1)

    def run_mode_4(self, i):
        time.sleep(1)

    def run_mode_5(self, i):
        time.sleep(1)

    def position_camera(self, position):
        print("position camera")

        if position == "vertical":
            self.pwm.start(10.5)
        elif self.camera_position == "horizontal":
            self.pwm.start(7.5)
        self.camera_position = position
        time.sleep(0.5)

    def take_picture(self):
        filename = str(time.time())+".jpg"

        filename_low = "data/low-"+filename
        filename_high = "data/high-"+filename

        print("take_picture "+self.camera_position+", filename"+filename_low)
        os.system("raspistill -h 300 -w 533 -o "+filename_low)
        os.system("raspistill -o "+filename_high)

        return filename_low

    def movie10s(self):
        print("10 sek movie "+self.camera_position)
        time.sleep(10)

    def send_picture(self, filename):
        print("send picture "+filename)
        os.system("mv "+filename+" data/send")