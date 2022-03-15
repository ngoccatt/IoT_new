import serial.tools.list_ports
import time
ser = serial.Serial(port="COM1", baudrate=115200)


def send_byte(string):
    for i in string:
        time.sleep(1)
        ser.write(str(i).encode())


while True:
    # send_byte("Hello")
    ser.flushInput()
    adc = ser.readline()

    adc = int(adc.decode().strip("!# \n"))
    print(adc)
    time.sleep(5)


