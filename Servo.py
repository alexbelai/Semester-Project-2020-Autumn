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
        self.pi.setmode(GPIO.BOARD)
        self.pi.setwarnings(False)
        # Setting the GPIO 18(12) as PWM Output 
        self.pi.setup(servo_pin, self.pi.OUT)
        # Setting 50hz on PWM pin (50hz specifically for servos)
        self.servo = self.pi.PWM(servo_pin, 50)
        self.servo.start(2.5)
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
        for i in range(120):
            self.servo.ChangeDutyCycle(i / 12 + 2.5)
            time.sleep(0.05)

    def turnLeft(self):
        """Returns to initial position of 0 degrees"""
        self.servo.ChangeDutyCycle(2.5)

    
    def turn90(self):
    	self.servo.ChangeDutyCycle(7.5)

servo = ServoController(GPIO, 11)
while True:
    print("Turning...")
    servo.turnRight()
    time.sleep(5)
    servo.turnLeft()
    time.sleep(5)
