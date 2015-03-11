#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import datetime
import os
import subprocess
import urllib
import random

buttonState = False
debounceDelay = 30
maxVolume = 100
playTime = 3

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def log(message):
	now = datetime.datetime.today()
	message = "%s/%s/%s %s:%s:%s - %s\n" % (now.year,now.month,now.day,now.hour,now.minute,now.second,message)
	logFile = open("/var/log/danceButton.log","a")
	logFile.write(message)
	print message

def playSong():
	log("Playing song")
	songs = os.listdir("/home/pi/scripts/dance_button/drops")
	#songs = ["badinga.mp3","boyohboy.mp3","whistle.mp3"]
	song = songs[random.randint(0,len(songs)-1)]
	os.popen("amixer -c 0 set PCM %s%%" % (maxVolume))
	os.popen('mpg321 /home/pi/scripts/dance_button/drops/%s &' % (song))

def fadeOut():
	log("Fading out")
	for i in range(maxVolume,0,-10):
		log("Setting PCM to %s" % (i))
		os.popen("amixer -c 0 set PCM %s%%" % (i))
		time.sleep(.1)
	log("setting to 0")
	os.popen("amixer -c 0 set PCM 0%")

def stopSong():
	log("Stopping song")
	#fadeOut()
	os.popen("killall mpg321")

def snapPhoto():
	log("Snapping Photo")
	photoName = str(int(time.time()))
	os.popen("raspistill -o /var/www/dancePhotos/%s.jpg &" % (photoName))

log("Staring up...")
offTime = time.time()
photo = False
while True:
	input_state = GPIO.input(18)

	if input_state == False and buttonState == True and photo == False:
		snapPhoto()
		photo = True

	if input_state == True:
			offTime = time.time() + playTime
			if random.randint(0,1000) == 500:
				log("Offtime: %s" % (offTime))

	if input_state == True and buttonState == False:
		if GPIO.input(18) == True:
			playSong()
			buttonState = True
		else:
			log("Debounce.  Not starting song.")


	if (time.time() > offTime) and buttonState == True:
		if GPIO.input(18) == False:
			stopSong()
			photo = False
			buttonState = False
		else:
			log("Debounce.  Not stopping song")
	
	if (int(time.time()) % 60 == 0):
		log("heartbeat") 
		time.sleep(1)
