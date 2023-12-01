import network
import time
import machine
from umqtt.simple import MQTTClient
from picozero import pico_temp_sensor, pico_led

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wind = False # raise bottle
unwind = False # drop bottle
mqttCheck = False # check for MQTT message
# Timer as to not overload the Pico with requests/receives
timer = machine.Timer(period = 2000, mode = machine.Timer.PERIODIC, callback = lambda t:mqttCheck = True)

DELAY = 0.01
STEPS = 200

LED = machine.Pin("LED",machine.Pin.OUT)

AIN1 = machine.Pin(17,machine.Pin.OUT)
AIN2 = machine.Pin(16,machine.Pin.OUT)
BIN1 = machine.Pin(14,machine.Pin.OUT)
BIN2 = machine.Pin(15,machine.Pin.OUT)

BTN = machine.Pin(3, machine.Pin.IN)

stepPos = 1
stepMax = 100
stepMin = 0
# dir = 1 # unused in this code

stepList = [[1,0,0,1],[0,1,0,1],[0,1,1,0],[1,0,1,0]] # [BIN2,BIN1,AIN2,AIN1]

while(not wlan.isconnected()):
    time.sleep(5)
    wlan.connect("#####","#####")

mqtt_server = '#####' # IP for MQTT server
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
            step()
            stepPos += 1
            client.publish(topic_pub3, 'Winding')
            client.publish(topic_pub2, '10')
        wind = False
        # maybe insert braking mechanism here?
    elif unwind:
        while stepPos > stepMin:
            step()
            stepPos -= 1
            client.publish(topic_pub4, 'Unwinding')
            client.publish(topic_pub1, '5')
            cleint.publish(topic_pub2, '20')
        unwind = False

    # temp = pico_temp_sensor.temp # here for reference
    # client.publish(topic_pub, str(temp).encode())
    