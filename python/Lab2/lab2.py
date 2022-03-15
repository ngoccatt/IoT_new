from cryptography.x509 import AccessDescription

print("Xin chào ThingsBoard")
import paho.mqtt.client as mqttclient
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import uuid

BROKER_ADDRESS = "mqttserver.tk"
'''
dia chi host trang web. co the lay source code cua 
thingboard roi tai len server tu tao, luc do 
minh se xai dia chi khac
'''
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "j1LspaO6a6TlFbHV8Tn1"
USERNAME = "bkiot"
PASSWORD = "12345678"

temp = 30
humi = 50
light_intensity = 100
counter = 0
oldData = ""
led = False
pump = False


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


# mqtt giong nhu 1 kenh youtube vay, muon nhan thong bao video moi thi phai
# subcribe vao no, de khi co video moi thi no se ba'o ve` lien
# (qua recv_message)

def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("UTF-8"))
    print("Topic: ", message.topic)
    global led, pump
    jsonobj = json.loads(message.payload)
    if "led" in message.topic:
        if jsonobj["status"] == "ON":
            led = True
        elif jsonobj["status"] == "OFF":
            led = False
    elif "pump" in message.topic:
        if jsonobj["status"] == "ON":
            pump = True
        elif jsonobj["status"] == "OFF":
            pump = False


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        # client.subscribe("#")
        # client.subscribe("/bkiot/1912750/status")
        client.subscribe("/bkiot/1912750/led")
        client.subscribe("/bkiot/1912750/pump")

    else:
        print("Connection is failed")


myUUID = str(uuid.uuid4())

client = mqttclient.Client("cat.tran03")
client.username_pw_set(USERNAME, PASSWORD)
# access token = username de dang nhap vao device.

client.on_connect = connected
# on_connect la 1 ham callback, khi ket 
# noi thanh cong thi no se chui vao ham
# connect (on_connect)
client.connect(BROKER_ADDRESS, 1883, keepalive=60)  # thuc hien ket noi.
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

json_data = {
    "temperature": 20,
    "humidity": 30
}

json_led_request = {
    "device": "LED",
    "status": "ON"
}

json_pump_request = {
    "device": "PUMP",
    "status": "ON"
}

# client.publish("/bkiot/1912750/led", json.dumps(json_led_request), 1, True)


# ------------------------------------main code--------------------------------------------------------
while True:
    temp = (temp + 1) % 100
    humi = (humi + 1) % 100
    json_data["temperature"] = temp
    json_data["humidity"] = humi
    # chu y truong retain = True, de du lieu duoc giu tren server va se thong bao toi cac client.
    # khi co client moi ket noi vao, no se ngay lap tuc duoc nhan du lieu luu tren server do khi subscribe
    client.publish("/bkiot/1912750/status", json.dumps(json_data), 1, True)
    print(f'led = {led}, pump = {pump}')
    time.sleep(10)
