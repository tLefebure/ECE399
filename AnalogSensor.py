# INCLUDES
import time
from machine import Pin

# GLOBALS
DELAY = 0.01
PI = 3.14
Radius = 0.01 # set this to the average radius of the coil in [m] (~1 cm)
MAG_FLAG = 0
EDGE_FLAG = 1

# OUTPUTs
LED = Pin("LED", Pin.OUT)

# INPUTS
MAG = Pin(12, Pin.IN)
TEMP = Pin(13, Pin.IN)

# FUNCTIONS
def lineLength(T_s,T_e,RPM):
        meters = radius * 2 * PI * RPM * (T_e - T_s) / 60 # Estimate reel length via (circumference * # of rotations)
        return meters

def RPM(T_s,T_e):
        RPS = T_e - T_s
        RPM = 60 * RPS
        return RPM
# SETUP
prevTEMP = TEMP.value() # intialize temp calculations with ambient temp before starting
print("Ambient TEMP[{}]".format(TEMP.value()))

# MAIN
while True:  # poll GPIO inputs at DELAY speed
        # Sensor polling for current loop
        currTEMP = TEMP.value()
        currMAG = MAG.value()
        print("MAG[{}], TEMP[{}]".format(currMAG,currTEMP))

        # Tempurature code
        diffTEMP = prevTEMP = currTEMP
        prevTEMP = currTEMP
        if(diffTEMP > 0): # change the 0 to some greater value to detect sudden changes
            print("\tTEMP increasing [{}]...".format(diffTEMP))
        elif(diffTEMP < 0):
            print("\tTEMP decreasing [{}]...".format(diffTEMP))

        # Magnet Sensor Code
        if(MAG.value()==0): # magnet near sensor
            print("Magnet detected!")
            if ((not MAG_FLAG) and EDGE_FLAG):
                    T_s = time.time()
                    MAG_FLAG = 1 # Magnet timer has started
                    EDGE_FLAG = 0 # Turn off EDGE_FLAG after first trigger to avoid multiple triggers while sensor value holds
            elif (MAG_FLAG and EDGE_FLAG): # on a magnet signal edge (edge = 1 to start)
                    T_e = time.time()
                    print("RPM[{}]".format(RPM(T_s,T_e)))
                    MAG_FLAG = 0 # Magnet timer has stopped
        elif(MAG.value()!=0): # magnet away from sensor
           EDGE_FLAG = 1 # Resensitize triggers to wait for next edge

        # Loop controls
        time.sleep(DELAY) # slow down execution if need be
        LED.toggle() # show how fast the loop is executing visually
