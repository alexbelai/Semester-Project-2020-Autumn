# Motor control class
# Parts of code based on the following blogs, tutorials, and codes:
#
#       Reefwing
#       https://gist.github.com/reefwing/5176087a2edb7425d5ddb9840ab72168

#import RPi.GPIO as GPIO
import time
from threading import Thread



class MotorController():
    """
    Class holding motors and their controls.
    """
    def __init__ (self, pi, motors):
        
        # Extract motors from list
        self.motors = motors
        self.pi = pi
        self.Left = self.motors[0]
        self.Right = self.motors[1]

        # Set up HBridge pins for Motors
        self.HBEnable12 = 0
        self.HBEnable34 = 0

        # sets GPIO mode to board, so that pins can be called by their numbers
        # pi.setmode(pi.BCM)
        
        #From main, pi is passed as GPIO

        pi.setup(self.HBEnable12, pi.OUT)
        pi.setup(self.HBEnable34, pi.OUT)
        pi.output(self.HBEnable12, 1)
        pi.output(self.HBEnable34, 1)

    # TODO:
    #def speed(self, cycle):
    #    """
    #    Sets duty cycle of all motors to given amount between 0-100%
    #    """
        
    
    def forward(self):
        """Sets all motors to move forward"""
        for motor in self.motors:
            motor.setForward()

    def backward(self):
        """Sets all motors to move backward"""
        for motor in self.motors:
            motor.setBackward()
    
    def right(self):
        """Turns right"""
        self.Left.setBackward()
        self.Right.setForward()

    def left(self):
        """Turns right"""
        self.Left.setForward()
        self.Right.setBackward()

    def stop(self):
        """Stops all motor activity"""
        for motor in self.motors:
            motor.stop()
    
    def cleanup(self):
        """Cleans pin states and stops signals going to motors"""
        self.pi.cleanup()
        #GPIO.cleanup() clears all pins from outputs Might not be needed here

class Stepper:

    def __init__ (self, pi, in1, in2, in3, in4):
        
        # Initialize control pin behavior
        self.pi = pi
        self.controlpins = [in1,in2,in3,in4]
        for pin in self.controlpins:
            pi.setup(pin, pi.OUT)
            pi.output(pin, 0)

        # Halfstep sequence for stepper motor movement, defines which pins need to be on at which step
        self.halfsequence = [
            [1,0,0,0],
            [1,1,0,0],
            [0,1,0,0],
            [0,1,1,0],
            [0,0,1,0],
            [0,0,1,1],
            [0,0,0,1],
            [1,0,0,1]
        ]

        self.fullsequence = [
            [1,0,0,0],
            [0,1,0,0],
            [0,0,1,0],
            [0,0,0,1],
        ]
        self.loopsize = len(self.fullsequence) # Defines the amount of steps a loop takes
    
    def clockwise(self, turns):
        """
        Runs "turns" amount of step loops clockwise in the motor.
        
        Note: There is no way to determine exact orientation of stepper once a loop has been made, make precise loops so you don't ruin motor orientation

        360 deg = 512 turns
        180 deg = 256 turns
        90 deg = 128 turns
        45 deg = 64 turns
        """
        for _ in range(turns):
            for step in range(self.loopsize): # For each step in the sequence
                for pin in range(4): # For each control pin
                    self.pi.output(self.controlpins[pin], self.fullsequence[step][pin])
                time.sleep(0.002) # 2 ms delay

class Motor:
    
    def __init__ (self, pi, forwardpin, backwardpin):
        
        self.pi = pi

        # Setting forward and backward control for motor
        self.forwardPin = forwardpin
        self.backwardPin = backwardpin

        # Set motor pins as output
        pi.setup(self.forwardPin, pi.OUT)
        pi.setup(self.backwardPin, pi.OUT)

        # Clear motor pins on init
        pi.cleanup()

    def getCurrentState(self):
        """Returns current state of motor pins in a tuple of 0s or 1s (forwardstate, backwardstate)"""
        return (self.pi.input(self.forwardPin), self.pi.input(self.backwardPin))

    def setForward(self):
        """Set forward pin of motor while turning off other pin"""
        self.pi.output(self.forwardPin, 1)
        self.pi.output(self.backwardPin, 0)

    def setBackward(self):
        """Set forward pin of motor while turning off other pin"""
        self.pi.output(self.backwardPin, 1)
        self.pi.output(self.forwardPin, 0)

    def stop(self):
        """Stops the given motor by clearing pins"""
        self.pi.output(self.forwardPin, 0)
        self.pi.output(self.backwardPin, 0)