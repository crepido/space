import RPi.GPIO as GPIO

import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7,GPIO.OUT)

p = GPIO.PWM(7,50)        #sets pin 21 to PWM and sends 50 signals per second
p.start(7.5)          #starts by sending a pulse at 7.5% to center the servo
try:                      
    while True:       #starts an infinite loop
        p.ChangeDutyCycle(4.5)    #sends a 4.5% pulse to turn the servo CCW
        time.sleep(0.5)                   #continues for a half a second
        p.ChangeDutyCycle(10.5)    #sends a 10.5% pulse to turn the servo CW
        time.sleep(0.5)                   #continues for a half a second
        p.ChangeDutyCycle(7.5)    #sends a 7.5% pulse to center the servo again
        time.sleep(0.5)                   #continues for a half a second
except KeyboardInterrupt:
    p.stop()
    GPIO.cleanup() 
