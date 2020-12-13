# Motor control class
# Parts of code based on the following blogs, tutorials, and codes:
#
#       Reefwing
#       https://github.com/suryasundarraj/rpi-series/blob/master/pwm_servo/servoPWM.py
#       

import RPi.GPIO as GPIO
import time

class ServoController():

    def __init__(self,pi,servo_pin):
        self.pi = pi
        # Setting the GPIO 18(12) as PWM Output 
        self.pi.setup(servo_pin,pi.OUT)
        # Setting 50hz on PWM pin (50hz specifically for servos)
        self.servo = pi.PWM(servo_pin,50)
        self.servo.start(0)
        """
        Period = 1/freq 
        Period @ 50hz  = 20 miliseconds
         
        

        full left = dutyCycle of 5%
        middle = dutyCycle of 7.5%
        full right = dutyCycle of 10% 

        *The values need to be tweeked 
        """

   # Changing the Duty Cycle to rotate the motor 
    def turnRight(self):
        self.servo.ChangeDutyCycle(12.5)
        #for i in range(12):
        #    self.servo.ChangeDutyCycle(i)

    def turnLeft(self):
        """Returns to initial position of 0 degrees"""
        self.servo.ChangeDutyCycle(2.5)

    
    def turn90(self):
    	self.servo.ChangeDutyCycle(7.5)
