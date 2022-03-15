print("Xin chào ThingsBoard")
import paho.mqtt.client as mqttclient
import time
import json
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

BROKER_ADDRESS = "localhost"
'''
dia chi host trang web. co the lay source code cua
thingboard roi tai len server tu tao, luc do
minh se xai dia chi khac
'''
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "j1LspaO6a6TlFbHV8Tn1"


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


# mqtt giong nhu 1 kenh youtube vay, muon nhan thong bao video moi thi phai
# subcribe vao no, de khi co video moi thi no se ba'o ve` lien
# (qua recv_message)

def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("UTF-8"))
    print(type(message.payload))
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'].find("setValue") != -1:
            print(jsonobj['params'])
            client.publish('v1/devices/me/attributes', json.dumps(jsonobj['params']), 1)
    except:
        print("problemmm")


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        # client.subscribe("#")
        client.subscribe("v1/devices/me/rpc/request/+")
        client.subscribe("v1/devices/me/attributes")
    else:
        print("Connection is failed")


def on_disconnected(client, userdata, rc):
    if rc == 0:
        print("Disconnect successfully")
        client.unsubcribe("v1/devices/me/rpc/response/+")
        client.unsubcribe("v1/devices/me/attributes")
    else:
        print("DISCONNECTED! SOMETHING WENT WRONG rc = " + str(rc))


myUUID = str(uuid.uuid4())

client = mqttclient.Client(myUUID)

client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)
# access token = username de dang nhap vao device.

client.on_connect = connected
# on_connect la 1 ham callback, khi ket
# noi thanh cong thi no se chui vao ham
# connect (on_connect)
client.on_subscribe = subscribed
client.on_message = recv_message
client.on_disconnect = on_disconnected
client.connect(BROKER_ADDRESS, 1883, keepalive=60)  # thuc hien ket noi.

client.loop_start()

requestdata = {
    'method': 'getTelemetry',
    'param': ""
}

requestAlldata = {
    "method": "getAllStat",
    "param": {}
}

client.publish('v1/devices/me/rpc/request/3', json.dumps(requestdata), 1)
client.publish("v1/devices/me/rpc/request/4", json.dumps(requestAlldata), 1)

setLed1Attr = {
    "led1": True
}

setPump1Attr = {
    "pump1": True
}

client.publish('v1/devices/me/attributes', json.dumps(setLed1Attr), 1)

client.publish('v1/devices/me/attributes', json.dumps(setPump1Attr), 1)
