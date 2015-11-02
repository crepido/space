import RPi.GPIO as GPIO

import time
import os

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7,GPIO.OUT)

p = GPIO.PWM(7,50)        #sets pin 21 to PWM and sends 50 signals per second
p.start(7.5)          #starts by sending a pulse at 7.5% to center the servo
try:                      
    while True:       #starts an infinite loop
        p.ChangeDutyCycle(4.5)    #sends a 4.5% pulse to turn the servo CCW
	os.system("raspistill -o test-"+str(time.time())+".jpg")
	time.sleep(30)	
	p.ChangeDutyCycle(10.5)    #sends a 10.5% pulse to turn the servo CW
	os.system("raspistill -o test-"+str(time.time())+".jpg")
	time.sleep(30)

except KeyboardInterrupt:
    p.stop()
    GPIO.cleanup() 
