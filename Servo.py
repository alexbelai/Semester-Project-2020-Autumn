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
        self.pi.setup(servo_pin, self.pi.OUT)
        
        # Setting 50hz on PWM pin (50hz specifically for servos)
        self.servo = self.pi.PWM(servo_pin, 50)
        self.servo.start(3)
        """
        Period = 1/freq 
        Period @ 50hz  = 20 miliseconds
         
        

        full left = dutyCycle of 5%
        middle = dutyCycle of 7.5%
        full right = dutyCycle of 10% 

        *The values need to be tweeked 
        """
    def change_dc(self, dc):
        self.servo.ChangeDutyCycle(dc)

   # Changing the Duty Cycle to rotate the motor 
    def turnRight(self):
        self.servo.ChangeDutyCycle(12.5)
        #for i in range(10):
        #    dc = i + 2.5
         #   print(f"{dc}")
         #   self.servo.ChangeDutyCycle(i + 2.5)
          #  time.sleep(2)

    def turnLeft(self):
        """Returns to initial position of 0 degrees"""
        #self.servo.ChangeDutyCycle(2.5)
        for i in range(10):
            dc = 12.5 - i
            print(f"{dc}")
            self.servo.ChangeDutyCycle(i + 2.5)
            time.sleep(2)

    
    def arm_up(self):
        for i in range(50):
            dc = 3 + (i * 0.09)
            print(f"{dc}")
            self.servo.ChangeDutyCycle(dc)
            time.sleep(0.1)#TESTING CODE
    
    def arm_down(self):
        for i in range(50):
            dc = 7.5 - (i * 0.09)
            print(f"{dc}")
            self.servo.ChangeDutyCycle(dc)
            time.sleep(0.1)#TESTING CODE
"""
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
servo = ServoController(GPIO, 11)
while True:
    print("Turning...")
    print(2.5)
    servo.change_dc(2.5)
    time.sleep(2)
    servo.change_dc(7)
    time.sleep(2)
    #servo.arm_up()
    #time.sleep(5)
    #servo.arm_down()

    print(4.5)
    servo.change_dc(4.5)
    time.sleep(2)
    print(5.5)
    servo.change_dc(5.5)
    time.sleep(2)
    print(6.5)
    servo.change_dc(6.5)
    time.sleep(2)
    print(7.5)
    servo.change_dc(7.5)
    time.sleep(2)
    print(8.5)
    servo.change_dc(8.5)
    time.sleep(2)
    print(9.5)
    servo.change_dc(9.5)
    time.sleep(2)
    print(10.5)
    servo.change_dc(10.5)
    time.sleep(2)
    print(11.5)
    servo.change_dc(11.5)
    time.sleep(2)
    print(12.5)
    servo.change_dc(12.5)
    time.sleep(2)
    #servo.turnLeft()
    #time.sleep(5)
"""