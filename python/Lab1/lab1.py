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

BROKER_ADDRESS = "localhost"
'''
dia chi host trang web. co the lay source code cua 
thingboard roi tai len server tu tao, luc do 
minh se xai dia chi khac
'''
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "j1LspaO6a6TlFbHV8Tn1"

temp = 30
humi = 50
light_intensity = 100
counter = 0
oldData = ""
led1 = False;
pump1 = False;


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


# mqtt giong nhu 1 kenh youtube vay, muon nhan thong bao video moi thi phai
# subcribe vao no, de khi co video moi thi no se ba'o ve` lien
# (qua recv_message)

def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("UTF-8"))
    print("Topic: ", message.topic)
    global oldData
    global led1, pump1
    # try:
    jsonobj = json.loads(message.payload)
    if jsonobj['method'].find("setValue") != -1:
        print(jsonobj['params'])
        for key in jsonobj["params"].keys():
            if key == "led1":
                led1 = jsonobj["params"]["led1"]
            elif key == "pump1":
                pump1 = jsonobj["params"]["pump1"]
        client.publish('v1/devices/me/attributes', json.dumps(jsonobj['params']), 1)
    elif jsonobj['method'].find("getAllStat") != -1:
        if oldData != message.payload:
            oldData = message.payload
            led1 = jsonobj["attribute"]["led1"]
            pump1 = jsonobj["attribute"]["pump1"]
        else:
            print("nothing new")
    # except:
    #     print("problemmm")


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        # client.subscribe("#")
        client.subscribe("v1/devices/me/rpc/request/+")
        client.subscribe("v1/devices/me/rpc/response/+")
    else:
        print("Connection is failed")


myUUID = str(uuid.uuid4())

client = mqttclient.Client("cat.tran03")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)
# access token = username de dang nhap vao device.

client.on_connect = connected
# on_connect la 1 ham callback, khi ket 
# noi thanh cong thi no se chui vao ham
# connect (on_connect)
client.connect(BROKER_ADDRESS, 1883, keepalive=60)  # thuc hien ket noi.
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

requestAlldata = {
    "method": "getAllStat",
    "param": {}
}

# ----------------------------------dia ly------------------------------------------
latitude = 10.8231
longitude = 106.6297
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)
driver.get('https://www.google.com')
# dong code duoi day dung de tao them 1 p co id = "location" chen vao trang web
# thuc te thi cac ham o day deu la ham async, nen ta khong the tra ve 1 gia tri nao ca
# kieu, khi goi ham async, thay vi cho async lam xong thi code di toi dong tiep theo luon
# con ham async chay trong background, khi nao no xong thi no goi ham callback
# navigator.geolocation.watchPosition() dung de lien tuc cap nhat vi tri cua nguoi dung 1 cach tu dong.
# chi can goi no 1 lan, no se lien tuc chay va cap nhat sau 1 khoang thoi gian nao do.
# moi khi no chay thanh cong, no se goi ham callback va thuc hien moi dong code trong ham callback do.

string = '''
    const para = document.createElement("p");
    para.innerHTML = "";
    para.id = "location";
    document.body.appendChild(para);
   function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.watchPosition(function(position) {
                var myjson = {"latitude":position.coords.latitude, "longitude":position.coords.longitude};
                console.log(position);
                console.log(position.coords.latitude);
                console.log(position.coords.longitude);
                var stringJson = JSON.stringify(myjson);
                console.log(stringJson);
                document.getElementById("location").innerHTML = stringJson;
            });
        } else {
            console.log("Geolocation is not supported by this browser.");
        }
    }
    getLocation();'''.replace('\n', '').replace('\t', '')

# repeat this code
try:
    # o day, minh chi execute doan javascript tren 1 lan, chu yeu de goi ham watchPosition 1 lan va de no tu chay
    # moi lan watchPosition chay xong, no se goi ham callback va ghi vao phan tu <p id="location"> doan Json
    # chua thong tin cua longitude va latitude.
    driver.execute_script(string)
    # cho 2s de doan script chay xong.
    time.sleep(2)
    # tim phan tu <p id="location"> de lay thong tin Json cua no.
    res = driver.find_element(By.ID, "location")
    # res la 1 webElement. lay noi dung cua no thi res.text
    loc = res.text
    # bien noi dung JSON dang string thanh dictionary.
    locDict = json.loads(loc)
    # lay thong tin tu locDict (type dictionary)
    longitude = locDict["longitude"]
    latitude = locDict["latitude"]
    print("latitude: %f, longitude: %f" % (locDict["latitude"], locDict["longitude"]))
except:
    print("Unable to get latitude and longitude")

# ------------------------------------main code--------------------------------------------------------
while True:
    collect_data = {'temperature': temp, 'humidity': humi, 'light': light_intensity,
                    'longitude': longitude, 'latitude': latitude}  # thang nay la dict
    # repeat code
    try:
        # driver.execute_script(string)
        # time.sleep(2)
        res = driver.find_element(By.ID, "location")
        loc = res.text
        locDict = json.loads(loc)
        longitude = locDict["longitude"]
        latitude = locDict["latitude"]
        print("latitude: %f, longitude: %f" % (locDict["latitude"], locDict["longitude"]))
    except:
        print("Unable to get latitude and longitude")
    # ---------------location--------------------------------
    temp = (temp + 1) % 100
    humi = (humi + 1) % 100
    light_intensity += 1
    # client.publish("v1/devices/me/rpc/request/4", json.dumps(requestAlldata), 1)
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    # print("oldData = ", oldData)
    print("led1 = ", led1, "pump1 = ", pump1)
    time.sleep(10)
