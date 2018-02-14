#!/usr/bin/env python3

from inputs import devices
from inputs import get_gamepad

while 1:
    events = get_gamepad()


    for event in events:
        lm = 0
        rm = 0
        print("Event type = " + event.ev_type + ", Event code = " + event.code + ", Event state = " + str(event.state))

        if event.code == 'ABS_Y':
            if event.state < 128: #moving forwards
                lm = (128-event.state)/128
                rm = (128-event.state)/128
            else:
                lm = (event.state-128)/128
                rm = (event.state-128)/128

        #Left/right movements override forward/backward movements
        if event.code == 'ABS_X':
            if event.state < 128: #analog to go left
                rm = (128-event.state)/128
            else:
                lm = (event.state-128)/128

    #print("Left motor = " + str(lm) + ", Right motor = " + str(rm))
