from time import gmtime, strftime, sleep
from datetime import datetime
from picamera import PiCamera

import requests
import RPi.GPIO as GPIO
import os
import subprocess
import os.path
import httplib, urllib
import atexit
import traceback
import logging
import time

# On exit
def exit_handler():
  GPIO.output(22, False)
  atexit.register(exit_handler)

# Logging
logger = logging.getLogger('doorbell')
hdlr = logging.FileHandler('/home/pi/Desktop/doorbell/web/doorbell.txt')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

# Start
print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " Doorbell started")
logger.info("Doorbell started")

# Pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.output(15, True)
GPIO.output(22, True)
GPIO.setup(11, GPIO.IN)

# Camera for Homebridge
cmdCamHomebridge='sudo modprobe bcm2835-v4l2'
subprocess.call(cmdCamHomebridge, shell=True)
camera = PiCamera()

# Loop
while 1:
  if not (GPIO.input(11)):
    try:
        time.sleep(0.01)
        if not (GPIO.input(11)):

            # Setup
            now=strftime("%Y-%m-%d %H:%M:%S", gmtime())
            filename=strftime("%Y-%m-%d_%H.%M.%S", gmtime())  + '.jpg'

            print(now + " Button pressed")
            logger.info("Button pressed")
            GPIO.output( 15, False)

            # Camera
            print("--> Camera")
            logger.info("--> Camera")
            camera.capture('/home/pi/Desktop/doorbell/web/photos/' +  filename)

            # Pushover
            print("--> Push")
            logger.info("--> Push")
            r = requests.post("https://api.pushover.net/1/messages.json", data = {
              "token": "myToken",
              "user": "myUser",
              "message": "Knock Knock Knock"
            },
            files = {
              "attachment": ("image.jpg", open('/home/pi/Desktop/doorbell/web/photos/' +  filename, "rb"), "image/jpeg")
            })
            print(r.text)

            # Finished
            print("--> Finished")
            logger.info("--> Finished")
            time.sleep(1)

    except Exception, e:
        logger.info(e)
        traceback.print_exc()
        logging.exception("!!!")
  else:
    GPIO.output( 15, True)
