import network
import time
import machine
from umqtt.simple import MQTTClient
from picozero import pico_temp_sensor, pico_led

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
led_status = False # off

while(not wlan.isconnected()):
    time.sleep(5)
    wlan.connect("StarNet","smedLey2")

mqtt_server = '10.0.0.250'
client_id = 'ECE399G19'
topic_pub = b'topic/hello'
topic_sub1 = b'topic/controltest'
topic_sub2 = b'topic/inputtest'
topic_msg = b'MQTT test for ECE 399 G19'

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
    global led_status
    if topic == topic_sub1 and msg:
        if not led_status:
            led_status = not led_status
            pico_led.on()
            print("LED on")
        else:
            led_status = not led_status
            pico_led.off()
            print("LED off")
    elif topic == topic_sub2:
        print(msg.decode())
   
try:
   client = mqtt_connect()
except OSError as e:
   reconnect()
   
sensor_temp = machine.ADC(4)
pico_led.off()
client.set_callback(callback)
client.subscribe(topic_sub1)
client.subscribe(topic_sub2)


while True:
    temp = pico_temp_sensor.temp
    client.publish(topic_pub, str(temp).encode())
    client.check_msg()
        
    time.sleep(1)
