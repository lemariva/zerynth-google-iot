# Google Cloud IoT Controlled publish period
# Created at 2017-10-03 08:49:48.182639

import streams
import json
from wireless import wifi

# import helpers functions to easily load keys and device configuration
import helpers

# choose a wifi chip supporting secure sockets
from espressif.esp32net import esp32wifi as wifi_driver

import requests
# import google cloud iot module
from googlecloud.iot import iot

from bosch.bmp180 import bmp180

# define a callback for config updates
def config_callback(config):
    global publish_period
    print('requested publish period:', config['publish_period'])
    publish_period = config['publish_period']
    return {'publish_period': publish_period}

# choose an appropriate way to get a valid timestamp (may be available through hardware RTC)
def get_timestamp():
    user_agent = {"user-agent": "curl/7.56.0"}
    return json.loads(requests.get('http://now.httpbin.org', headers=user_agent).content)['now']['epoch']

# wifi configuration
SSID = ""
WPA2Pass = ""
# device key file
new_resource('private.hex.key')
# device configuration json file
new_resource('device.conf.json')

# place here your wifi configuration
print("Establishing Link...")
streams.serial()
wifi_driver.auto_init()
try:
    wifi.link(SSID,wifi.WIFI_WPA2,WPA2Pass)
except Exception as e:
    print("ooops, something wrong while linking :(", e)
    while True:
        sleep(1000)

myip = wifi.link_info()[0]
print('Connected with IP:', myip)

# load key
pkey = helpers.load_key('private.hex.key')
# load configuration
device_conf = helpers.load_device_conf()
publish_period = 5000

# configuring sensor
print('Connecting to BMP120')
bmp = bmp180.BMP180(I2C0)
bmp.start()
bmp.init()

print('Registering device.')
device = iot.Device(device_conf['project_id'], device_conf['cloud_region'], device_conf['registry_id'], device_conf['device_id'], pkey, get_timestamp)
try:
    # create a google cloud device instance, connect to mqtt broker, set config callback and start mqtt reception loop
    device.mqtt.connect()
    device.on_config(config_callback)
    device.mqtt.loop()
except Exception as e:
    print("ooops, something wrong while registering the device :(", e)
    while True:
        sleep(1000)

print('Starting to publishing.')
idx = 0
while True:
    temp, pres = bmp.get_temp_pres() # Read both (temperature and pressure)
    print("Temp: ", temp, "C and Pres:", pres, "Pa")

    print('Publish random sample.')
    try:
        device.publish_event(json.dumps({ 'sample_id': idx,
                                          'temperature': temp,
                                          'pressure': pres,
                                          'timestamp': get_timestamp()
        }))
    except Exception as e:
        print("ooops, something wrong while publishing event:(", e)
    idx = idx + 1
    sleep(publish_period)
