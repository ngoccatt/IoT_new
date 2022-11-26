from softTimer import *
import time
from stopAndWaitARQ import *
import paho.mqtt.client as mqttclient
import json
import uuid


COMMAND_LED_OFF         = 0
COMMAND_LED_ON          = 1
COMMAND_PUMP_OFF        = 2
COMMAND_PUMP_ON         = 3


BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "NM4ZJdbSG37xO0lnkCBP"

def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")

def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    cmd = 99
    #TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            #DO STUFF
            if jsonobj["params"] == True:
                cmd = COMMAND_LED_ON
            elif jsonobj["params"] == False:
                cmd = COMMAND_LED_OFF
            temp_data = {"led": jsonobj["params"]}

        if jsonobj['method'] == "setFan":
            #DO STUFF
            if jsonobj["params"] == True:
                cmd = COMMAND_PUMP_ON
            elif jsonobj["params"] == False:
                cmd = COMMAND_PUMP_OFF
            temp_data = {"fan": jsonobj["params"]}

        client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1, True)
    except:
        pass
    addMqttMessage(str(cmd))

def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")

def sendToAda(mess):
    id, name, value = mess.split(":")
    data = {}
    if name == "TEMP":
        # print("send temp:", value)
        data = {"temperature": int(value)}
    elif name == "LIGHT":
        # print("send light:", value)
        data = {"light": int(value)}
    # print(name)
    client.publish("v1/devices/me/telemetry", json.dumps(data), 1, True)


myID = str(uuid.uuid4())
client = mqttclient.Client(myID)
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

initTimer()
setTimer(0, 1000)

initPort("COM1")

while True:
    if checkFlag(0) == 1:
        # print(time.strftime("%H:%M:%S"))
        readSerial()
        # receive serial info from board (temp, humid...) and send ack
        stopAndWaitFSM_Receiver(sendToAda)
        # receive ack and send command to board (led, pump...) (
        stopAndWaitFSM_Sender()
        setTimer(0, 1000)
    # print("hello")
    runTimer(0)
    time.sleep(0.01)
