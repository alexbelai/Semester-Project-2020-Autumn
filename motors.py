"""
Class that contains most of motor controls
"""
import RPI.GPIO as GPIO

class Motor():
    def __init__ (self, forwardpin, backwardpin):
        self.forwardpin = forwardpin
        self.backwardpin = backwardpin

class MotorController():
    def __init__ (self):
        