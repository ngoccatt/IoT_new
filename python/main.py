import paho.mqtt.client as mqttclient
import time
import json
import serial.tools.list_ports
import sys

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "a5H028HksIpjzGTtELkk"


def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        print(strPort)
        if "ELTIMA Virtual Serial Port" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
            return commPort
    return commPort


coom = getPort()

# for python, it should get the first port
ser = serial.Serial(port=getPort(), baudrate=115200)
if ser.isOpen():
    print("Port is opened")


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def send_byte(string):
    for i in string:
        # send tu tu de stm32 bat thi duoc. send
        # 1 cuc nhanh qua, stm32 bat ko kip
        # the nen moi lan send, minh sleep 1 giay nay :<
        ser.write(str(i).encode())
        time.sleep(1)





def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))

    temp_data = {'value': True}
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setValue":
            temp_data['value'] = jsonobj['params']
            # ser.write((temp_data['value'] + "#").encode())
            if temp_data['value']:
                send_byte("!LED:ON#")
            else:
                send_byte("!LED:OFF#")
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
    except:
        print("WTF")


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




temp = 30
humi = 50
light_intesity = 100
adc = 0
counter = 0
while True:
    collect_data = {'temperature': temp, 'humidity': humi, 'light': light_intesity, 'adc':adc}
    # phia tren la dinh dang json
    temp += 1
    humi += 1
    light_intesity += 1
    ser.flushInput()
    adc = ser.readline()    #day la 1 ham blocking: no se block cho toi khi nao
    # nhan duoc nguyen 1 string ket thuc boi \n
    adc = int(adc.decode().strip("!# \n"))
    print(adc)
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)

    time.sleep(5)




