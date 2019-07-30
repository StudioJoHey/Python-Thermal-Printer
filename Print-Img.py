from __future__ import print_function
import RPi.GPIO as GPIO
import subprocess, time, socket
from PIL import Image
from Adafruit_Thermal import *

printer = Adafruit_Thermal("/dev/serial0", 9600, timeout=5)

# Use Broadcom pin numbers (not Raspberry Pi pin numbers) for GPIO
GPIO.setmode(GPIO.BCM)

IMAGE = Image.open('IMG/PostkarteBlume2.jpg')
IMAGE_90 = IMAGE.rotate(90, expand=True)

# Print greeting image
printer.printImage(IMAGE_90, True)
printer.feed(3)
