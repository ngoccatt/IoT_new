import random

from softTimer import *
import time
from stopAndWaitARQ import *
import uuid

def turnOffPeripheral(mess):
    # in implementation, the only thing that send to microbit is 0, 1, 2 or 3
    cmd = int(mess)
    if cmd == 0:
        print("LED: TURN OFF")
    elif cmd == 1:
        print("LED: TURN ON")
    elif cmd == 2:
        print("FAN: TURN OFF")
    elif cmd == 3:
        print("FAN: TURN ON")

initTimer()
setTimer(0, 1000)
setTimer(1, 5000)

TEMP = 0
LIGHT = 1
state = TEMP

initPort("COM2")

while True:
    if checkFlag(0) == 1:
        # print(time.strftime("%H:%M:%S"))
        readSerial()
        # receive serial info from gateway (led, pump), turn off led or smth and send ack
        stopAndWaitFSM_Receiver(turnOffPeripheral)
        # when stimulus appear, send serial. then wait for ack
        stopAndWaitFSM_Sender()
        setTimer(0, 1000)
    if checkFlag(1) == 1:
        if state == TEMP:
            id = 1
            name = "TEMP"
            value = random.randint(1, 100)
            message = f'{id}:{name}:{value}'
            addMqttMessage(message)
            state = LIGHT
        elif state == LIGHT:
            id = 1
            name = "LIGHT"
            value = random.randint(1, 100)
            message = f'{id}:{name}:{value}'
            addMqttMessage(message)
            state = TEMP
        setTimer(1, 5000)
    # print("hello")
    runTimer(1)
    runTimer(0)
    time.sleep(0.01)
