import random

print("IoT Gateway")
import paho.mqtt.client as mqttclient
import time
import json
import serial.tools.list_ports
import uuid

COMMAND_LED_OFF         = 0
COMMAND_LED_ON          = 1
COMMAND_PUMP_OFF        = 2
COMMAND_PUMP_ON         = 3

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
mess = ""

#TODO: Add your token and your comport
#Please check the comport in the device manager
THINGS_BOARD_ACCESS_TOKEN = "NM4ZJdbSG37xO0lnkCBP"
bbc_port = "COM7"
if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)

def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    data = {}
    if splitData[1] == "TEMP":
        data = {"temperature": int(splitData[2])}
    elif splitData[1] == "LIGHT":
        data = {"light": int(splitData[2])}

    print(data)
    if len(data) > 0:
        client.publish("v1/devices/me/telemetry", json.dumps(data), 1, True)
    #TODO: Add your source code to publish data to the server

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
    temp_data = {'value': True}
    cmd = 99
    #TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            #DO STUFF
            # print(type(jsonobj["params"]["led"]))
            for key in jsonobj["params"]:
                if jsonobj["params"][key] == True:
                    cmd = COMMAND_LED_ON
                elif jsonobj["params"][key] == False:
                    cmd = COMMAND_LED_OFF

        if jsonobj['method'] == "setFan":
            #DO STUFF
            for key in jsonobj["params"]:
                if jsonobj["params"][key] == True:
                    cmd = COMMAND_PUMP_ON
                elif jsonobj["params"][key] == False:
                    cmd = COMMAND_PUMP_OFF

        temp_data = jsonobj["params"]
        client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1, True)
    except:
        pass
    print("send to board: " + str(cmd) + "#")
    if len(bbc_port) > 0:
        ser.write((str(cmd) + "#").encode())

def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")

myID = str(uuid.uuid4())
client = mqttclient.Client(myID)
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

temperature = light = 0
while True:

    if len(bbc_port) > 0:
        readSerial()
    # temperature = random.randint(0, 100)
    # light = random.randint(0, 100)
    # data = {"temperature": temperature, "light": light}
    # client.publish("v1/devices/me/telemetry", json.dumps(data), 1, True)
    time.sleep(1)

