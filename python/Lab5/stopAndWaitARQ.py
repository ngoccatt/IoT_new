import random
import serial

COMPORT = ""

ser = 0

def initPort(port):
    global ser, COMPORT
    COMPORT = port
    if len(COMPORT) > 0:
        ser = serial.Serial(port=COMPORT, baudrate=115200)


globalMessage = ""

# message from server that "kick" the sender
mqttMessage = []
# ack message from serial
ACKMessage = []
# serial message from serial
serialMessage = []

WAIT_SENT_0 = 0
WAIT_ACK_1 = 1
WAIT_SENT_1 = 2
WAIT_ACK_0 = 3

WAIT_0 = 0
WAIT_1 = 1

MAX_TIME_OUT_REPEAT = 5
TIMEOUT_PERIOD = 3

seqNum_send = 0
seqNum_recv = 0
senderState = WAIT_SENT_0
receiverState = WAIT_0

timeOutCnt = TIMEOUT_PERIOD
timeOutFlag = 0
timeOutRepeat = MAX_TIME_OUT_REPEAT

bufferedMessage = ""

def runTimeOut():
    global timeOutCnt, timeOutFlag
    if timeOutCnt > 0:
        timeOutCnt = timeOutCnt - 1
        if timeOutCnt == 0:
            timeOutFlag = 1
            
def startTimeOut():
    global timeOutCnt, timeOutFlag, timeOutRepeat
    timeOutCnt = TIMEOUT_PERIOD
    timeOutFlag = 0

def stopTimeOut():
    global timeOutCnt, timeOutFlag
    timeOutCnt = -1
    timeOutFlag = 0


#message: !seq.1:TEMP:30#
def sendMessage(message):
    global bufferedMessage
    if bufferedMessage == "":
        bufferedMessage = message
    ss = f'!{seqNum_send}.{bufferedMessage}#'
    print(f"Sending serial: {ss}")
    ser.write(ss.encode())
    # startTimeOut()

def sendAck():
    ss = f'!{seqNum_recv}.ACK#'
    print(f"Sending ack: {ss}")
    ser.write(ss.encode())

def addMqttMessage(mess):
    global mqttMessage
    mqttMessage.append(mess)

def addAck(mess):
    global ACKMessage
    ACKMessage.append(mess)

def addSerialMessage(mess):
    global serialMessage
    serialMessage.append(mess)


# func: receive a function to do the processing if this Receiver receives
# serial message.
def stopAndWaitFSM_Receiver(func):
    global receiverState, seqNum_recv
    if len(serialMessage) > 0:
        seq, mess = serialMessage.pop(0).split(".")
        if receiverState == WAIT_0:
            if seq == "0":
                print("Received: " + seq + "." + mess)
                #xu ly gui len gia tri nhiet do/do am len thingsboard (gateway)
                # id, name, value = mess.split(":")
                #todo
                func(mess)
                #xu ly hien thi den (microbit)
                #todo
                receiverState = WAIT_1
                seqNum_recv = 1 - seqNum_recv
            sendAck()

        elif receiverState == WAIT_1:
            if seq == "1":
                print("Received: " + seq + "." + mess)
                #xu ly gui len gia tri nhiet do/do am len thingsboard (gateway)
                #todo
                func(mess)
                #xu ly hien thi den (microbit)
                #todo
                receiverState = WAIT_0
                seqNum_recv = 1 - seqNum_recv
            sendAck()
        else:
            print("Send nudes")
        

# check mqttMessage array. if the array is not empty, this function try to send each item in the array
# add message to the array by using addMqttMessage(message:string)
def stopAndWaitFSM_Sender():
    global seqNum_send, senderState, timeOutCnt, timeOutRepeat, timeOutFlag, bufferedMessage
    global mqttMessage, ACKMessage
    if senderState == WAIT_SENT_0:
        # wait to send a packet with seq = 0
        # buffer message should be empty before sending new message.
        bufferedMessage = ""
        timeOutRepeat = MAX_TIME_OUT_REPEAT
        # temp = random.randint(0,100)
        # mess = f'1:TEMP:{temp}'
        if len(mqttMessage) > 0:
            sendMessage(mqttMessage.pop(0))
            senderState = WAIT_ACK_1
            startTimeOut()
            print("state 1 to 2")

        pass
    elif senderState == WAIT_ACK_1:
        if timeOutFlag == 1:
            timeOutFlag = 0

            #resend message
            sendMessage("")

            timeOutRepeat = timeOutRepeat - 1
            startTimeOut()
            if timeOutRepeat == 0:
                senderState = WAIT_SENT_0
                print(f'ERROR: CAN NOT SEND {bufferedMessage}')

        # seq, mess = readSerial(ser_send)
        if len(ACKMessage) > 0:
            seq, mess = ACKMessage.pop().split(".")
            if seq == "1" and mess == "ACK":
                seqNum_send = 1 - seqNum_send
                senderState = WAIT_SENT_1
                stopTimeOut()
                timeOutRepeat = MAX_TIME_OUT_REPEAT
        pass
    elif senderState == WAIT_SENT_1:
        # wait to send a packet with seq = 1
        # buffer message should be empty before sending new message.
        bufferedMessage = ""
        timeOutRepeat = MAX_TIME_OUT_REPEAT
        # temp = random.randint(0, 100)
        # mess = f'1:HUMID:{temp}'
        if len(mqttMessage) > 0:
            sendMessage(mqttMessage.pop(0))
            senderState = WAIT_ACK_0
            startTimeOut()
            print("state 3 to 4")
        pass
    elif senderState == WAIT_ACK_0:
        if timeOutFlag == 1:
            timeOutFlag = 0

            # resend message
            sendMessage("")

            timeOutRepeat = timeOutRepeat - 1
            startTimeOut()
            if timeOutRepeat == 0:
                senderState = WAIT_SENT_1
                print(f'ERROR: CAN NOT SEND {bufferedMessage}')

        # seq, mess = readSerial(ser_send)
        if len(ACKMessage) > 0:
            seq, mess = ACKMessage.pop().split(".")
            if seq == "0" and mess == "ACK":
                seqNum_send = 1 - seqNum_send
                senderState = WAIT_SENT_0
                stopTimeOut()
                timeOutRepeat = MAX_TIME_OUT_REPEAT
        pass
    runTimeOut()


def readSerial():
    global globalMessage, ACKMessage, serialMessage
    bytesToRead = ser.inWaiting()
    if bytesToRead > 0:
        globalMessage = globalMessage + ser.read(bytesToRead).decode("utf-8")
        while ("!" in globalMessage) and ("#" in globalMessage):
            start = globalMessage.find("!")
            end = globalMessage.find("#")
            mess = globalMessage[start+1:end]
            # mess se gom seq.message
            # print(mess)
            if "ACK" in mess:
                ACKMessage.append(mess)
            else:
                serialMessage.append(mess)
            if end == len(globalMessage) - 1:
                globalMessage = ""
            else:
                globalMessage = globalMessage[end+1:]
