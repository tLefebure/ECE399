import network
import time
import machine
from umqtt.simple import MQTTClient
from picozero import pico_temp_sensor, pico_led

# GLOBALS
DELAY = 0.01
PI = 3.14
Radius = 0.01 # set this to the average radius of the coil in [m] (~1 cm)
MAG_FLAG = 0
EDGE_FLAG = 1
STEPS = 200

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wind = False # raise bottle
unwind = False # drop bottle
mqttCheck = False # check for MQTT message
# Timer as to not overload the Pico with requests/receives
timer = machine.Timer(period = 2000, mode = machine.Timer.PERIODIC, callback = lambda t:mqttCheck = True)

LED = machine.Pin("LED",machine.Pin.OUT)

AIN1 = machine.Pin(17,machine.Pin.OUT)
AIN2 = machine.Pin(16,machine.Pin.OUT)
BIN1 = machine.Pin(14,machine.Pin.OUT)
BIN2 = machine.Pin(15,machine.Pin.OUT)

MAG = machine.Pin(12, machine.Pin.IN)

BTN = machine.Pin(3, machine.Pin.IN)

stepPos = 1
stepMax = 100
stepMin = 0
# dir = 1 # unused in this code

stepList = [[1,0,0,1],[0,1,0,1],[0,1,1,0],[1,0,1,0]] # [BIN2,BIN1,AIN2,AIN1]

# FUNCTIONS
def lineLength(T_s,T_e,RPM):
        meters = radius * 2 * PI * RPM * (T_e - T_s) / 60 # Estimate reel length via (circumference * # of rotations)
        return meters

def RPM(T_s,T_e):
        RPS = T_e - T_s
        RPM = 60 * RPS
        return RPM

while(not wlan.isconnected()):
    time.sleep(5)
    wlan.connect("ECE399G19Demo","ECE399G19Demo")

mqtt_server = '192.168.225.124' # IP for MQTT server
client_id = 'ECE399G19'
# Add sub and pub topics here
topic_pub1 = b'topic/power'
topic_pub2 = b'topic/rpm'
topic_pub3 = b'topic/winding'
topic_pub4 = b'topic/unwinding'
topic_sub1 = b'topic/motorControlWind'
topic_sub2 = b'topic/motorControlUnwind'
topic_msg = b'MQTT test for ECE 399 G19'

def step():
        step=stepList[stepPos % 4]
        AIN1.value(step[3])
        AIN2.value(step[2])
        BIN1.value(step[1])
        BIN2.value(step[0])
        time.sleep(DELAY)
        

def mqtt_connect():
       client = MQTTClient(client_id, mqtt_server,1883,"ECE399G19", "ECE399G19", keepalive=3600)
       client.connect()
       print('Connected to %s MQTT Broker'%(mqtt_server))
       return client
    
def reconnect():
   print('Failed to connect to the MQTT Broker. Reconnecting...')
   time.sleep(5)
   machine.reset()
   
def callback(topic, msg):
    global wind, unwind
    if topic == topic_sub1:
        wind = True
    elif topic == topic_sub2:
        unwind = True
   
try:
   client = mqtt_connect()
except OSError as e:
   reconnect()
   
# sensor_temp = machine.ADC(4)
client.set_callback(callback)
# Subscribe to published topics
client.subscribe(topic_sub1)
client.subscribe(topic_sub2)


while True:

    if(mqttCheck):
        client.check_msg()

    if wind:
        while stepPos < stepMax:
            currMAG = MAG.value()
            step()
            stepPos += 1
            if(MAG.value()==0): # magnet near sensor
                print("Magnet detected!")
                if ((not MAG_FLAG) and EDGE_FLAG):
                    T_s = time.time()
                    MAG_FLAG = 1 # Magnet timer has started
                    EDGE_FLAG = 0 # Turn off EDGE_FLAG after first trigger to avoid multiple triggers while sensor value holds
                elif (MAG_FLAG and EDGE_FLAG): # on a magnet signal edge (edge = 1 to start)
                    T_e = time.time()
                    RPM = RPM(T_s,T_e)
                    Length += LineLength(T_s,T_e,RPM) # ASSUMES SINGLE ROTATIONAL DIRECTION! Multiply by 'dir' variable if switching rotation
                    print("RPM[{}], Length[{}]".format(RPM,Length))
                    MAG_FLAG = 0 # Magnet timer has stopped
            elif(MAG.value()!=0): # magnet away from sensor
               EDGE_FLAG = 1 # Resensitize triggers to wait for next edge
            client.publish(topic_pub3, 'Winding')
            client.publish(topic_pub2, RPM.str.encode())
        wind = False
        # maybe insert braking mechanism here?
    elif unwind:
        while stepPos > stepMin:
            currMAG = MAG.value()
            step()
            stepPos -= 1
            if(MAG.value()==0): # magnet near sensor
                print("Magnet detected!")
                if ((not MAG_FLAG) and EDGE_FLAG):
                    T_s = time.time()
                    MAG_FLAG = 1 # Magnet timer has started
                    EDGE_FLAG = 0 # Turn off EDGE_FLAG after first trigger to avoid multiple triggers while sensor value holds
                elif (MAG_FLAG and EDGE_FLAG): # on a magnet signal edge (edge = 1 to start)
                    T_e = time.time()
                    RPM = RPM(T_s,T_e)
                    Length += LineLength(T_s,T_e,RPM) # ASSUMES SINGLE ROTATIONAL DIRECTION! Multiply by 'dir' variable if switching rotation
                    print("RPM[{}], Length[{}]".format(RPM,Length))
                    MAG_FLAG = 0 # Magnet timer has stopped
            elif(MAG.value()!=0): # magnet away from sensor
               EDGE_FLAG = 1 # Resensitize triggers to wait for next edge
            client.publish(topic_pub2, RPM.str.encode())
            client.publish(topic_pub4, 'Unwinding')
            client.publish(topic_pub1, '5')
        unwind = False

    # temp = pico_temp_sensor.temp # here for reference
    # client.publish(topic_pub, str(temp).encode())
    
