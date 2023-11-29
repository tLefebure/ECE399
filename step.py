# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Use this example for digital pin control of an H-bridge driver
# like a DRV8833, TB6612 or L298N.

# Make sure to: pip3 install adafruit-circuitpython-motor


import time
from machine import Pin

DELAY = 0.01
STEPS = 200

LED = Pin("LED",Pin.OUT)

AIN1 = Pin(17,Pin.OUT)
AIN2 = Pin(16,Pin.OUT)
BIN1 = Pin(14,Pin.OUT)
BIN2 = Pin(15,Pin.OUT)

BTN = Pin(3, Pin.IN)

stepPos = 0

stepList = [[1,0,0,0],[0,0,0,1],[0,1,0,0],[0,0,1,0]]
step = [stepList[0]]
brake = [1,1,1,1]

def step():
        step=stepList[stepPos % 4]
        AIN1.value(step[3])
        AIN2.value(step[2])
        BIN1.value(step[1])
        BIN2.value(step[0])
        time.sleep(DELAY)
        #print(step)
        
while True:
    if(BTN.value()):
        step()
        stepPos+=1
        LED.toggle()
        print(step)        
    else:
        AIN1.value(1)
        AIN2.value(1)
        BIN1.value(1)
        BIN2.value(1)
        print("Brake!")
        LED.value(0)
        
    

