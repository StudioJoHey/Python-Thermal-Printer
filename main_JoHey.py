#!/usr/bin/python

# Main script for Adafruit Internet of Things Printer 2.  Monitors button
# for taps and holds, performs periodic actions (Twitter polling by default)
# and daily actions (Sudoku and weather by default).
# Written by Adafruit Industries.  MIT license.
#
# MUST BE RUN AS ROOT (due to GPIO access)
#
# Required software includes Adafruit_Thermal, Python Imaging and PySerial
# libraries. Other libraries used are part of stock Python install.
#
# Resources:
# http://www.adafruit.com/products/597 Mini Thermal Receipt Printer
# http://www.adafruit.com/products/600 Printer starter pack

from __future__ import print_function
import RPi.GPIO as GPIO
import subprocess, time, socket
from PIL import Image
from Adafruit_Thermal import *

nextInterval = 0.0   # Time of next recurring twitter operation
nextInstaInterval = 0.0
nextInstaInterval2 = 0.0 
nextRSSInterval1 = 0.0
nextRSSInterval2 = 0.0
dailyFlag    = False # Set after daily trigger occurs
lastId       = '1'   # State information passed to/from interval script
lastPostDateStr = "01.01.2019_00:00:00"
lastPostDateStr2 = "01.01.2019_00:00:00"
lastPostDateWeb1Str = "01.01.2019_00:00:00"
lastPostDateWeb2Str = "01.01.2019_00:00:00"
printer      = Adafruit_Thermal("/dev/serial0", 9600, timeout=5)


# Called at periodic intervals (30 seconds by default).
# Invokes twitter script.
def twitterInterval():
  p = subprocess.Popen(["python3", "twitter_JoHey.py", str(lastId)],
                       stdout=subprocess.PIPE)
  return p.communicate()[0] # Script pipes back lastId, returned to main

def instaInterval():
  p = subprocess.Popen(["python3", "RSS-insta.py", str(lastPostDateStr)],
                       stdout=subprocess.PIPE)
  return p.communicate()[0] # Script pipes back lastPostDateStr, returned to main

def instaInterval2():
  p = subprocess.Popen(["python3", "RSS-insta2.py", str(lastPostDateStr2)],
                       stdout=subprocess.PIPE)
  return p.communicate()[0] # Script pipes back lastPostDateStr, returned to main

def RSSIntervalWeb():
  p = subprocess.Popen(["python3", "RSS-familien.py", str(lastPostDateWeb1Str)],
                       stdout=subprocess.PIPE)
  return p.communicate()[0]

def RSSIntervalWeb2():
  p = subprocess.Popen(["python3", "RSS-fb-afip.py", str(lastPostDateWeb2Str)],
                       stdout=subprocess.PIPE)
  return p.communicate()[0] 


# Called once per day (6:30am by default).
# Invokes weather forecast and sudoku-gfx scripts.
##def daily():
##  subprocess.call(["python", "forecast.py"])
##  subprocess.call(["python", "sudoku-gfx.py"])


# Initialization

# Use Broadcom pin numbers (not Raspberry Pi pin numbers) for GPIO
GPIO.setmode(GPIO.BCM)

# Processor load is heavy at startup; wait a moment to avoid
# stalling during greeting. Standart: (30)
time.sleep(30)

# Show IP address (if network is available)
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))
    printer.feed(1)
except:
    printer.boldOn()
    printer.println('Network is unreachable.')
    printer.boldOff()
    printer.feed(3)
    exit(0)

# Print greeting image
printer.print('"PinnwandConnection" ist ein \nProjekt von studio-johey.de')
printer.feed(1)
printer.printImage(Image.open('JoHey_Black_ThermoPrint.jpg'), True)
printer.feed(3)

# Main loop
while(True):
  # Poll current time
    t = time.time()

  # Once per day (currently set for 6:30am local time, or when script
  # is first run, if after 6:30am), run forecast and sudoku scripts.
##  l = time.localtime()
##  if (60 * l.tm_hour + l.tm_min) > (60 * 8 + 00):
##    if dailyFlag == False:
##      daily()
##      dailyFlag = True
##  else:
##    dailyFlag = False  # Reset daily trigger
   
    if t > nextInstaInterval: #IT WORKS!!!
        nextInstaInterval = t + 60
        result_i = instaInterval()
        if result_i is not None:
            #print("result_i:" + result_i)
            lastPostDateStr = str(result_i.rstrip(b'\r\n'))
            lastPostDateStr = lastPostDateStr[2:-1]
            print("lastPostDateStr Insta: " + lastPostDateStr)
            
    time.sleep(10)

  # Every 30 seconds, run Twitter scripts.  'lastId' is passed around
  # to preserve state between invocations.  Probably simpler to do an
  # import thing.
    if t > nextInterval:
        nextInterval = t + 30.0
        result_t = twitterInterval()
        if result_t is not None:
              lastId = str(result_t.rstrip(b'\r\n'))
              lastId = lastId[2:-1]
              print("lastTwitterID: " + lastId)
              

    time.sleep(10)

    if t +30 > nextRSSInterval1: #ItWorks!
        nextRSSInterval1 = t + 60 *60
        result = RSSIntervalWeb()
        if result is not None:
              lastPostDateWeb1Str = str(result.rstrip(b'\r\n'))
              lastPostDateWeb1Str = lastPostDateWeb1Str[2:-1]
              print("lastPostDateStr Web1Famil: " + lastPostDateWeb1Str)
             
              
    if t > nextRSSInterval2: #It Works!!!
        nextRSSInterval2 = t + 60.0 * 5
        result_i = RSSIntervalWeb2()
        if result_i is not None:
            lastPostDateWeb2Str = str(result_i.rstrip(b'\r\n'))
            lastPostDateWeb2Str = lastPostDateWeb2Str[2:-1]
            print("lastPostDateStr Web2FB: " + lastPostDateWeb2Str)
            
        
    time.sleep(10) #reduces stress on CPU, esp
    
    if t > nextInstaInterval2: #IT WORKS!!!
        nextInstaInterval2 = t + 60 *5
        result_i = instaInterval2()
        if result_i is not None:
            #print("result_i:" + result_i)
            lastPostDateStr2 = str(result_i.rstrip(b'\r\n'))
            lastPostDateStr2 = lastPostDateStr2[2:-1]
            print("lastPostDateStr2 Insta: " + lastPostDateStr2)
                

              

