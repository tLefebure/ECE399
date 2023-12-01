# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Use this example for digital pin control of an H-bridge driver
# like a DRV8833, TB6612 or L298N.

import time
from machine import Pin

DELAY = 0.01
prevTEMP = 0

LED = Pin("LED", Pin.OUT)

MAG = Pin(12, Pin.IN)
TEMP = Pin(13, Pin.IN)


while True:  # poll GPIO inputs at DELAY speed
        currTEMP = TEMP.value()
        currMAG = MAG.value()
        print("MAG[{}], TEMP[{}]".format(currMAG,currTEMP))
        diffTEMP = prevTEMP = currTEMP
        prevTEMP = currTEMP
        if(diffTEMP > 0): #change the 0 to some greater value to detect sudden changes
            print("TEMP increasing...")
        if(MAG.value()==0):
            print("Magnet detected!")
            # use time.time() to count seconds and estimate RPM based on magnet events
        time.sleep(DELAY)
        LED.toggle()
    
