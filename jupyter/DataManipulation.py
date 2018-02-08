#!/usr/bin/env python3

import csv
import pandas as pd
import numpy as np
import mdp

class DataManipulation:

    def __init__(self, filename):
        self.__data = pd.read_csv(filename)
        self.__NUM_OF_BINS = 10
        self.__total = 0
        self.__total_motor = None
        self.__total_sensor = None
        self.__total_us = None
        self.__pcanodes = None
        self.__DIMENSION = 6            
        self.__first_array_bin = np.arange(0, self.__NUM_OF_BINS)
        self.__second_array_bin = np.arange(0, (self.__NUM_OF_BINS**2), self.__NUM_OF_BINS)
        self.__third_array_bin = np.arange(0, (self.__NUM_OF_BINS**3), self.__NUM_OF_BINS**2)
        self.__fourth_array_bin = np.arange(0, (self.__NUM_OF_BINS**4), self.__NUM_OF_BINS**3)
        self.__fifth_array_bin = np.arange(0, (self.__NUM_OF_BINS**5), self.__NUM_OF_BINS**4)
        self.__sixth_array_bin = np.arange(0, (self.__NUM_OF_BINS**6), self.__NUM_OF_BINS**5)
        
    """Normalizing motor values

    Normalized the left and right motor values ranging from -1000 to 1000, to be from -1 to 1
    """
    def normalized_motor(self):
        self.__data['right motor'] = self.__data['right motor'].values/1000 #min -1 max 1
        self.__data['left motor'] = self.__data['left motor'].values/1000 #min -1 max 1

    """Normalizing values ranging from 0 to 1
    
    Normalized all sensor, motor and ultrasound values to be in range from 0 to 1.
    """
    def normalized_0_to_1(self):
        self.__total_motor = (0.5*((self.__data['left motor'].values + self.__data['right motor'].values)/2) + 0.5) * self.__NUM_OF_BINS
        self.__total_sensor = ((self.__data['left sensor'].values + self.__data['right sensor'].values) / 2)  * self.__NUM_OF_BINS
        self.__total_us = ((self.__data['left ultrasound sensor'].values + self.__data['right ultrasound sensor'].values) / 2)  * self.__NUM_OF_BINS
        
        for i in range(len(self.__total_motor)):
            if self.__total_motor[i] == self.__NUM_OF_BINS:
                self.__total_motor[i] = self.__NUM_OF_BINS-1

            if self.__total_sensor[i] == self.__NUM_OF_BINS:
                self.__total_sensor[i] == self.__NUM_OF_BINS-1

            if self.__total_motor[i] == self.__NUM_OF_BINS:
                self.__total_motor[i] == self.__NUM_OF_BINS-1

        self.__total_motor = np.floor(self.__total_motor).astype(int)
        self.__total_sensor = np.floor(self.__total_sensor).astype(int)
        self.__total_us = np.floor(self.__total_us).astype(int)

        return self.__total_motor,self.__total_sensor,self.__total_us

    def get_NUM_OF_BINS(self):
        return self.__NUM_OF_BINS

    def set_NUM_OF_BINS(self, NUM_OF_BINS):
        self.__NUM_OF_BINS = NUM_OF_BINS

    def get_data(self):
        return self.__data

    def get_total_motor(self):
        return self.__total_motor

    def get_total_sensor(self):
        return self.__total_sensor

    def get_total_us(self):
        return self.__total_us

    def normalized_minus1_to_1(self):
        pass

    def get_dimension(self):
        return self.__DIMENSION

    """Converting the total values to bin number
    
    Count the total with the formula
    DIM1 * (NOB * DIM2) * ((NOB**2) * DIM3)

    If there is no third dimension, it would just count until the second dimension.
    """
    def convert_values_to_bins(self, firstDimension=None, secondDimension=None, thirdDimension=None,
                                fourthDimension=None, fifthDimension=None, sixthDimension=None):
        if self.__total is not 0:
            self.__total = 0

        if firstDimension is not None: 
            self.__total += firstDimension 
        if secondDimension is not None:
            self.__total += self.__NUM_OF_BINS * secondDimension
        if thirdDimension is not None:
            self.__total += (self.__NUM_OF_BINS**2) * thirdDimension
        if fourthDimension is not None:
            self.__total += (self.__NUM_OF_BINS**3) * fourthDimension
        if fifthDimension is not None:
            self.__total += (self.__NUM_OF_BINS**4) * fifthDimension
        if sixthDimension is not None:
            self.__total += (self.__NUM_OF_BINS**5) * sixthDimension

        self.__total = np.floor(self.__total).astype(int)
        return self.__total

    """Removing transition where state goes to itself.
        
    To remove where state goes to itself (e.g A A A A B will be reduced to A B)
    """
    def remove_continous_state(self, arr=None):
        if arr is None:
            temp = [self.__total[i] for i in range(len(self.__total)-1) if self.__total[i] != self.__total[i+1]]
            if len(temp) == 0:
                temp.append(self.__total[-1])
            elif temp[-1] != self.__total[-1]:
                temp.append(self.__total[-1])
            return np.array(temp)
        else:
            temp = [arr[i] for i in range(len(arr)-1) if arr[i] != arr[i+1]]
            if len(temp) == 0:
                temp.append(arr[-1])
            elif temp[-1] != arr[-1]:
                temp.append(arr[-1])
            return np.array(temp)

    """Make a dictionary inside a dictionary from transition array without frequency
    
    This detects how many times a state goes to another state. 
    Represented with a dictionary in a dictionary. (e.g {A : {B: 2}} means bin A moves to bin B 2 times.)
    """
    def transition_frequency(self, transition_array):
        transition_with_frequency = {}
        for i in range(len(transition_array)-1):
            if transition_array[i] not in transition_with_frequency:
                transition_with_frequency[transition_array[i]] = {}
                transition_with_frequency[transition_array[i]][transition_array[i+1]] = 1

            elif transition_array[i+1] in transition_with_frequency[transition_array[i]]:
                transition_with_frequency[transition_array[i]][transition_array[i+1]] += 1

            elif transition_array[i+1] not in transition_with_frequency[transition_array[i]]:
                transition_with_frequency[transition_array[i]][transition_array[i+1]] = 1

        return transition_with_frequency

    """Translate a transition with frequency dictionary to transition array with frequency
    
    This is to make a new list where every 3 values indicate source, destination, and frequency visited.
    """
    def most_visited_state_transition(self, transition_with_frequency):
        most_visited_state = []
        for i,j in transition_with_frequency.items():
            most_visited_state.append(i)
            most_visited_state.append(sorted(j.items(),key=lambda t: t[1], reverse=True)[0][0])
            most_visited_state.append(sorted(j.items(),key=lambda t: t[1], reverse=True)[0][1])

        return np.array(most_visited_state)

    """Separate values into arrays of bins
    
    Take the array values and digitize it to bins to determine which bin each value belongs to.
    """
    def digitize_total_values(self, to_be_digitized, type):

        if type == '2d':
            #numpy digitize assigns bin from 1 to 10.  but we want to use 0 to 9    
            xArray = np.digitize(to_be_digitized % self.__NUM_OF_BINS, self.__first_array_bin) - 1
            yArray = np.digitize(to_be_digitized, self.__second_array_bin) - 1

            return xArray, yArray
        elif type == '3d':
            #numpy digitize assigns bin from 1 to 10.  but we want to use 0 to 9
            xArray = np.digitize(to_be_digitized % self.__NUM_OF_BINS, self.__first_array_bin) - 1
            yArray = np.digitize(to_be_digitized % (self.__NUM_OF_BINS**2), self.__second_array_bin) - 1
            zArray = np.digitize(to_be_digitized, self.__third_array_bin) - 1

            return xArray, yArray, zArray

    def digitize_cycle(self, to_be_digitized):
        xArray = np.digitize(to_be_digitized % self.__NUM_OF_BINS, self.__first_array_bin) - 1 # ls
        yArray = np.digitize(to_be_digitized % (self.__NUM_OF_BINS**2), self.__second_array_bin) - 1 #rs
        zArray = np.digitize(to_be_digitized % (self.__NUM_OF_BINS**3), self.__third_array_bin) - 1 #lus
        wArray = np.digitize(to_be_digitized % (self.__NUM_OF_BINS**4), self.__fourth_array_bin) - 1#rus
        uArray = np.digitize(to_be_digitized % (self.__NUM_OF_BINS**5), self.__fifth_array_bin) - 1 #lm
        vArray = np.digitize(to_be_digitized , self.__sixth_array_bin) - 1 #rm
        return xArray, yArray, zArray, wArray, uArray, vArray