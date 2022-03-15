import sys
import random
import time
import json
from Adafruit_IO import MQTTClient
import serial.tools.list_ports




#----------------------------------------SERIAL COMMUNICATION-----------------------------------
'''
Cac thuoc tinh cua device:
humid, temperature, LDR, door, gas la thuoc tinh dang input, se doc len server
LED, curtain, conditioner la thuoc tinh output, do minh dieu khien
'''
device_info = {"humid": 0, "temperature": 0,
               "LDR": {"1": 0, "2": 0, "3": 0, "4": 0},
               "LED": {"0": 0, "1": 0, "2": 0, "3": 0},
               "curtain": 0,
               "door": 0,
               "conditioner": {"power": 0, "temp": 22},
               "gas": 0}

'''
moi khi gui command, ong hay set bien nay ve 0. cho cho toi khi device gui ve OK, nghia la
device da thuc hien xong cong viec, bien nay se duoc set len 1.
ong chi goi ham gui command khi bien nay = 1. neu bien nay = 0, ong khong nen gui command toi device.
'''
device_ready = 1


#danh sach cac ham gui command ve board.
'''
gui serial command de bat den theo cac che do khac nhau
LedIndex: [0,3]
mode: [0,3] -> 0:tat, 1:sang den trai, 2:sang den phai, 3:sang 2 den
'''
def set_led(ledIndex, mode):
    command = "!setLed:" + str(ledIndex) + ":" + str(mode) + "*"
    print(command)
    ser.write(command.encode())

'''
gui serial command de dong mo rem cua
mode: [0,2] -> 0:dong rem, 1:mo rem 1 nua, 2:mo het rem.
'''
def set_curtain(mode):
    command = "!setCurtain:" + str(mode) + "*"
    print(command)
    ser.write(command.encode())


'''
gui serial command de tat mo may lanh
is_on: [0,1] -> 0: tat may lanh, 1: mo may lanh
'''
def set_conditioner_power(is_on):
    command = "!setConditioner:" + str(is_on) + "*"
    print(command)
    ser.write(command.encode())


'''
gui serial command de chinh nhiet do may lanh
temp: [0,99]
'''
def set_conditioner_temp(temp):
    command = "!setConditionerTemp:" + str(temp) + "*"
    print(command)
    ser.write(command.encode())


def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    comPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        # print(strPort)  -> COM3 - USB-SERIAL CH340 (COM3)
        # dung lenh sau neu ket noi board that
        # if "USB-SERIAL" in strPort:
        # dung lenh sau neu dung port ao
        if "Virtual Serial Port" in strPort:
            splitPort = strPort.split(" ")
            comPort = splitPort[0]
            # print(comPort)
    return comPort


def print_data():
    global device_info
    print("---------------------------------------------------------------------")
    print("temperature = ", device_info["temperature"])
    print("humid = ", device_info["humid"])
    print("LDR1 = ", device_info["LDR"]["1"], "; LDR2 = ", device_info["LDR"]["2"],
          "\r\nLDR3 = ", device_info["LDR"]["3"], "; LDR4 = ", device_info["LDR"]["4"])
    print("LED0 = ", device_info["LED"]["0"], "; LED1 = ", device_info["LED"]["1"],
          "\r\nLED2 = ", device_info["LED"]["2"], "; LED3 = ", device_info["LED"]["3"])
    print("curtain = ", device_info["curtain"])
    print("door = ", device_info["door"])
    print("conditioner: power = ", device_info["conditioner"]["power"], " temp = ", device_info["conditioner"]["temp"])
    print("gas = ", device_info["gas"])


'''
 message kieu: !abc*
 xu ly du lieu. Neu du lieu nhan duoc la chuoi json chua thong tin, loads no vao device_info
 Neu nhan duoc !OK*, set device_ready = 1.
 '''
def processData(data=""):
    data = data.replace("!", "")
    data = data.replace("*", "")
    global device_info
    global device_ready
    if data == "OK":
        device_ready = 1
        print("device ready")
    else:
        device_info = json.loads(data)


serial_message = ""

'''
Kiem tra du lieu serial duoc truyen qua UART, neu co du lieu
tien hanh processData
'''
def read_serial():
    bytesToRead = ser.inWaiting()
    if bytesToRead > 0:
        global serial_message
        serial_message += ser.read(bytesToRead).decode("UTF-8")
        # print(serial_message)
        while ("!" in serial_message) and ("*" in serial_message):
            start = serial_message.find("!")
            end = serial_message.find("*")
            processData(serial_message[start:end + 1])
            if end == len(serial_message):
                serial_message = ""
            else:
                serial_message = serial_message[end + 1:]
    else:
        # print("nothing here")
        pass


ser = serial.Serial(port=getPort(), baudrate=9600)
print(getPort())

#----------------------------------------SERIAL COMMUNICATION-----------------------------------

#----------------------------------------MQTT---------------------------------------------------

AIO_FEED_ID = ["bbc-led", "bbc-temp"]
AIO_USERNAME = "ngoccatt"
AIO_KEY = "aio_axOx85Mj3lEZZyssufHzvd9EvXQx"


def connected(client):
    print("Ket noi thanh cong...")
    for key in AIO_FEED_ID:
        client.subscribe(key)


def subscribe(client, userdata, mid, granted_qos):
    print("Subcribed")


def disconnected(client):
    print("Ngat ket noi...")
    sys.exit(1)


def message(client, feed_id, payload):
    print("Received: " + payload + " from " + feed_id)

client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()

#----------------------------------------MQTT---------------------------------------------------


i = 0
while True:
    read_serial()
    i = (i + 1) % 5
    if i == 0:
        print_data()
    time.sleep(1)
    # value = random.randint(0, 100)
    # print("Cap nhat : ", value)
    # client.publish("bbc-temp", value)
    # time.sleep(30)
