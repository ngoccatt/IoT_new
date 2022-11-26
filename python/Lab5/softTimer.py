NUM_OF_TIMER  = 3
counter = []
timerFlag = []
PERIOD_MS = 10

def initTimer():
    global timerFlag, counter
    for i in range(0, NUM_OF_TIMER):
        timerFlag.append(0)
        counter.append(0)

def runTimer(index):
    global counter, timerFlag
    if counter[index] > 0:
        counter[index] = counter[index] - 1
        if counter[index] == 0:
            timerFlag[index] = 1

def setTimer(index, duration_s):
    global counter, timerFlag
    counter[index] = duration_s / PERIOD_MS
    timerFlag[index] = 0

def checkFlag(index):
    return timerFlag[index]

