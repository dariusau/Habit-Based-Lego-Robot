#!/usr/bin/env python3

import socket
from ev3dev.ev3 import *
from time import sleep
import pickle
import threading
from Ev3devSetup import Ev3devSetup
import Constant
import time
import random
import subprocess


# ============================================
# A thread class from https://www.tutorialspoint.com/python/python_multithreading.htm
# This thread class represents a background thread on the robot to collect sensor-motor data and send it back
# to the server.

class SensorBackgroundThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        while True:
            sensorValues(self.name)

def cleanup():
    print('cleaning up...')
    mySocket.close()
    print("Socket closed")
    subprocess.call("./stopmotors")
    print("Motor stopped")
    print('quiting')
    exit()

# =============================================

#Setting up with MAX_SENSOR, MAX_MOTOR, BIAS, SENSOR_GAIN, OUTPUT_GAIN
ev3devrobot = Ev3devSetup()

motor_left = ev3devrobot.initLargeMotor('outB')
motor_left.reset()

motor_right = ev3devrobot.initLargeMotor('outC')
motor_right.reset()

left_colour_sensor = ev3devrobot.initColorSensor('in2')
left_colour_sensor.mode = 'COL-AMBIENT'

right_colour_sensor = ev3devrobot.initColorSensor('in3')
right_colour_sensor.mode = 'COL-AMBIENT'

left_ultrasonic_sensor = ev3devrobot.initUltraSonicSensor('in1')
left_ultrasonic_sensor.mode = 'US-DIST-CM'

right_ultrasonic_sensor = ev3devrobot.initUltraSonicSensor('in4')
right_ultrasonic_sensor.mode = 'US-DIST-CM'

# ==== ROBOT MOVEMENT FUNCTIONS === #
# ==============================================

def forward():
    motor_right.run_timed(speed_sp=450, time_sp=100)
    motor_left.run_timed(speed_sp=450,time_sp=100)

# ==============================================

def back():
    motor_right.run_timed(speed_sp=-450, time_sp=100)
    motor_left.run_timed(speed_sp=-450, time_sp=100)


# ==============================================

def left():
    motor_right.run_timed(speed_sp=450, time_sp=100)
    motor_left.run_timed(speed_sp=-450, time_sp=100)


# ==============================================

def right():
    motor_right.run_timed(speed_sp=-450, time_sp=100)
    motor_left.run_timed(speed_sp=450, time_sp=100)


# ==============================================

def stopMotor():
    motor_left.stop()
    motor_right.stop()

# ==============================================

def sendPackages(package):
    dataString = pickle.dumps(package)
    mySocket.send(dataString)
    

# ==== DATA COLLECTION FUNCTIONS ==== #
# ==============================================

def keyboardControl():

    # Get original time as a basis to run the following code every n seconds (where n <= 0.1)
    starttime = time.time()
    packageSize = 0
    package = []

    while True:
        ## normalized to lie between 0 and 1 (1 close, 0 far)
        lsv = ev3devrobot.SENSOR_GAIN * float(left_colour_sensor.value()) / ev3devrobot.MAX_SENSOR
        rsv = ev3devrobot.SENSOR_GAIN * float(right_colour_sensor.value()) / ev3devrobot.MAX_SENSOR

        luv = 1.0 - max(0.0, min(1.0, float(left_ultrasonic_sensor.value()) / 200.0))
        ruv = 1.0 - max(0.0, min(1.0, float(right_ultrasonic_sensor.value()) / 200.0))

        Leds.set(Leds.LEFT, brightness_pct=lsv)
        Leds.set(Leds.RIGHT, brightness_pct=rsv)

        lmv = motor_left.speed
        rmv = motor_right.speed
        package.extend([lsv, rsv, luv, ruv, lmv, rmv])

        packageSize += 1
        if packageSize == Constant.PACKAGE_SIZE:
            sendPackages(package)
            packageSize = 0
            package = []

        time.sleep(0.05 - ((time.time() - starttime) % 0.05))

def braitenburgMovement():

    # Get original time as a basis to run the following code every n seconds (where n <= 0.1)
    starttime = time.time()
    it = 0
    packageSize = 0
    package = []

    while True:
        ## normalized to lie between 0 and 1 (1 close, 0 far)
        lsv = ev3devrobot.SENSOR_GAIN * float(left_colour_sensor.value()) / ev3devrobot.MAX_SENSOR
        rsv = ev3devrobot.SENSOR_GAIN * float(right_colour_sensor.value()) / ev3devrobot.MAX_SENSOR

        luv = 1.0 - max(0.0, min(1.0, float(left_ultrasonic_sensor.value()) / 200.0))
        ruv = 1.0 - max(0.0, min(1.0, float(right_ultrasonic_sensor.value()) / 200.0))

        Leds.set(Leds.LEFT, brightness_pct=lsv)
        Leds.set(Leds.RIGHT, brightness_pct=rsv)

        ## AGGR
        lmv = ev3devrobot.BIAS + rsv - 0.0 * lsv - (ruv * 2.)
        rmv = ev3devrobot.BIAS + lsv - 0.0 * rsv - (luv * 2.)

        lmv *= ev3devrobot.OUTPUT_GAIN
        rmv *= ev3devrobot.OUTPUT_GAIN

        if max(lmv, rmv) > ev3devrobot.MAX_MOTOR:
            lmv -= max_mv - ev3devrobot.MAX_MOTOR
            rmv -= max_mv - ev3devrobot.MAX_MOTOR


        if (it % 10) == 0:
            print('ls: %0.3f rs:%0.3f lm: %0.3f rm:%0.3f' % (lsv, rsv, lmv, rmv))

        lmv = int(max(-1000, min(1000, ev3devrobot.MAX_MOTOR * lmv)))
        rmv = int(max(-1000, min(1000, ev3devrobot.MAX_MOTOR * rmv)))

        motor_left.run_forever(speed_sp=lmv)
        motor_right.run_forever(speed_sp=rmv)


        package.extend([lsv, rsv, luv, ruv, lmv, rmv])
        packageSize += 1
        if packageSize == Constant.PACKAGE_SIZE:
            sendPackages(package)
            packageSize = 0
            package = []

        time.sleep(0.05 - ((time.time() - starttime) % 0.05))

def randomMovement():
    it = 0
    # Get original time as a basis to run the following code every n seconds (where n <= 0.1)
    starttime = time.time()
    buttonValues = {0: "Forward", 1: "Back", 2: "Left", 3: "Right"}
    packageSize = 0
    package = []

    while True:
        it += 1
        lsv = ev3devrobot.SENSOR_GAIN * float(left_colour_sensor.value()) / ev3devrobot.MAX_SENSOR
        rsv = ev3devrobot.SENSOR_GAIN * float(right_colour_sensor.value()) / ev3devrobot.MAX_SENSOR

        luv = 1.0 - max(0.0, min(1.0, float(left_ultrasonic_sensor.value()) / 200.0))
        ruv = 1.0 - max(0.0, min(1.0, float(right_ultrasonic_sensor.value()) / 200.0))

        Leds.set(Leds.LEFT, brightness_pct=lsv)
        Leds.set(Leds.RIGHT, brightness_pct=rsv)

        ## AGGR
        lmv = ev3devrobot.BIAS + rsv - 0.0 * lsv - (ruv * 2.)
        rmv = ev3devrobot.BIAS + lsv - 0.0 * rsv - (luv * 2.)

        lmv *= ev3devrobot.OUTPUT_GAIN
        rmv *= ev3devrobot.OUTPUT_GAIN

        if max(lmv, rmv) > ev3devrobot.MAX_MOTOR:
            lmv -= max_mv - ev3devrobot.MAX_MOTOR
            rmv -= max_mv - ev3devrobot.MAX_MOTOR

        if (it % 10) == 0:
            print('ls: %0.3f rs:%0.3f lm: %0.3f rm:%0.3f' % (lsv, rsv, lmv, rmv))

        lmv = int(max(-1000, min(1000, ev3devrobot.MAX_MOTOR * lmv)))
        rmv = int(max(-1000, min(1000, ev3devrobot.MAX_MOTOR * rmv)))

        # get random number to determine if the robot is going to move forward, back, right or left
        num = random.randrange(4)
        positivespeed = random.randrange(500)
        negativespeed = -random.randrange(500)

        if num == 0:
            motor_left.run_timed(speed_sp=positivespeed, time_sp=10000)
            motor_right.run_timed(speed_sp=positivespeed, time_sp=10000)
        elif num == 1:
            motor_left.run_timed(speed_sp=negativespeed, time_sp=10000)
            motor_right.run_timed(speed_sp=negativespeed, time_sp=10000)
        elif num == 2:
            motor_left.run_timed(speed_sp=positivespeed, time_sp=10000)
            motor_right.run_timed(speed_sp=negativespeed, time_sp=10000)
        elif num == 3:
            motor_left.run_timed(speed_sp=negativespeed, time_sp=10000)
            motor_right.run_timed(speed_sp=positivespeed, time_sp=10000)

        package.extend([lsv, rsv, luv, ruv, lmv, rmv])
        packageSize += 1
        if packageSize == Constant.PACKAGE_SIZE:
            sendPackages(package)
            packageSize = 0
            package = []

        time.sleep(0.05 - ((time.time() - starttime) % 0.05))

# ==============================================

def startNewThread(name):
    # Create a new daemon thread just for taking in sensory-motor values
    thread1 = SensorBackgroundThread(1, "Thread-1", 1)
    thread1.daemon = True
    thread1.start()
# ==============================================

# Code is based on https://stackoverflow.com/questions/41294848/python-sockets-how-to-connect-between-two-computers-on-the-same-wifi
def Main():
    #Host IP is IPv4 address of the computer found basedy Connection Information on Linux
    #host = '192.168.1.66'
    host = Constant.IP_ADDRESS
    port = 5000
    global mySocket
    print("Creating socket")
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.connect((host, port))
    print("Socket connected to {0}".format(host))


    movementType = int(mySocket.recv(1).decode())
    if movementType == 1:
        keyboardThread = threading.Thread(target=keyboardControl)
        keyboardThread.daemon = True
        keyboardThread.start()
        print("1 is chosen")
        while True:
            k = mySocket.recv(2048).decode()
            #print('Received from server: ' + k, flush=True)
            if k == 'w':
                forward()
            elif k == 's':
                back()
            elif k == 'a':
                left()
            elif k == 'd':
                right()
            elif k == 'p':
                stop()
            elif k == 'q':
                break
    
    elif movementType == 2:
        braitenburgThread = threading.Thread(target=braitenburgMovement)
        braitenburgThread.daemon = True
        braitenburgThread.start()
        print("2 is chosen")
        while True:
            k = mySocket.recv(2048).decode()
            if k == 'q':
                break

    elif movementType == 3:
        randomThread = threading.Thread(target=randomMovement)
        randomThread.daemon = True
        randomThread.start()
        print("3 is chosen")
        while True:
            k = mySocket.recv(2048).decode()
            if k == 'q':
                break

    # Commands received from the server are translated into actual robot movements
    cleanup()
    # Close the socket after the program has quit from the server side


if __name__ == '__main__':
    Main()