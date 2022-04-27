print("IoT Gateway")
import paho.mqtt.client as mqttclient
import time
import json
import serial.tools.list_ports

import random

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
mess = ""

LED_ON  = 0
LED_OFF = 1
FAN_ON  = 2
FAN_OFF = 3


#TODO: Add your token and your comport
#Please check the comport in the device manager
THINGS_BOARD_ACCESS_TOKEN = "jMLIodZd0prPq3QZqtnO"
bbc_port = ""
if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)

def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    #TODO: Add your source code to publish data to the server
    if (splitData[1] == "TEMP"):
        TEMP_json = {"temperature": splitData[2]}
        client.publish('v1/devices/me/telemetry', json.dumps(TEMP_json), 1, True)

    elif (splitData[1] == "LIGHT"):
        LIGHT_json = {"light": splitData[2]}
        client.publish('v1/devices/me/telemetry', json.dumps(LIGHT_json), 1, True)

def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")

def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    # temp_data = {'value': True}
    cmd = 0
    #TODO: Update the cmd to control 2 devices
    try:
        # load: decode json -> object
        # dump: encode object -> json
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            # update cmd (to send to board)
            if (jsonobj['params'] == True):
                cmd = LED_ON
            else:
                cmd = LED_OFF
            # publish status of LED to server
            temp_data = {"led": jsonobj['params']}
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1, True)

        if jsonobj['method'] == "setFAN":
            # update cmd (to send to board)
            if (jsonobj['params'] == True):
                cmd = FAN_ON
            else:
                cmd = FAN_OFF
            # publish status of FAN to server
            temp_data = {"fan": jsonobj['params']}
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1, True)
    except:
        pass

    if len(bbc_port) > 0:
        ser.write((str(cmd) + "#").encode())

def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

while True:

    if len(bbc_port) >  0:
        readSerial()

    time.sleep(1)