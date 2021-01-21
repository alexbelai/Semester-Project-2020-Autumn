# Motor control class
# Parts of code based on the following blogs, tutorials, and codes:
#
#       Reefwing
#       https://gist.github.com/reefwing/5176087a2edb7425d5ddb9840ab72168

#import RPi.GPIO as GPIO
import time
from threading import Thread
import RPi.GPIO as GPIO


class MotorController():
    """
    Class holding motors and their controls.
    """
    def __init__ (self, pi, stby, motors):
        
        # Extract motors from list
        self.motors = motors
        self.pi = pi
        self.Left = self.motors[0]
        self.Right = self.motors[1]
        
        # Set motor speed ratio
        self.Left.set_speed(4)
        self.Right.set_speed(11.25)

        # Set up HBridge pins for Motors
        self.stby = 36

        # Write 1 to STDBY
        pi.setup(self.stby, pi.OUT)
        pi.output(self.stby, 1)
        
    def backward(self):
        """Sets all motors to move backward"""
        for motor in self.motors:
            motor.setForward()

    def forward(self):
        """Sets all motors to move forward"""
        for motor in self.motors:
            motor.setBackward()

    def stop(self):
        """Stops all motor activity"""
        for motor in self.motors:
            motor.stop()
            
    def bit_right(self):
        """Orients the robot a bit right, used by IR sensors to maintain line tracking"""
        self.Right.setBackward()
        time.sleep(0.3)
        self.Right.stop()
        return
    
    def bit_left(self):
        """Orients the robot a bit left, used by IR sensors to maintain line tracking"""
        self.Left.setBackward()
        time.sleep(0.3)
        self.Left.stop()
        return
    
    def turn_ccw(self):
        """Turns the robot 90 degrees counter-clockwise."""
        self.Left.setBackward()
        self.Right.setForward()
        time.sleep(3)
        self.Left.stop()
        self.Right.stop()
        return
    
    def turn_cw(self):
        """Turns the robot 90 degrees counter-clockwise."""
        self.Left.setForward()
        self.Right.setBackward()
        time.sleep(3)
        self.Left.stop()
        self.Right.stop()
        return
    
    def cleanup(self):
        """Cleans pin states and stops signals going to motors"""
        self.pi.cleanup()

    def turn(self, cur_dir, des_dir):
        """Orients the robot from current direction to desired direction."""
        if cur_dir == "down":
            if des_dir == "right":
                self.turn_ccw()
                return
            elif des_dir == "up":
                self.turn_cw()
                self.turn_cw()
                return
            elif des_dir == "left":
                self.turn_cw()
                return
        elif cur_dir == "right":
            if des_dir == "down":
                self.turn_cw()
                return                
            elif des_dir == "up":
                self.turn_ccw()
                return
            elif des_dir == "left":
                self.turn_cw()
                self.turn_cw()
                return
        elif cur_dir == "up":
            if des_dir == "down":
                self.turn_cw()
                self.turn_cw()
                return
            elif des_dir == "right":
                self.turn_cw()
                return
            elif des_dir == "left":
                self.turn_ccw()
                return
        elif cur_dir == "left":
            if des_dir == "down":
                self.turn_ccw()
                return
            elif des_dir == "right":
                self.turn_cw()
                self.turn_cw()
                return
            elif des_dir == "up":
                self.turn_cw()
                return


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

        360 deg = 528 turns
        180 deg = 264 turns
        90 deg = 132 turns
        45 deg = 66 turns
        """
        for i in range(turns):
            for step in range(self.loopsize): # For each step in the sequence
                for pin in range(4): # For each control pin
                    self.pi.output(self.controlpins[pin], self.fullsequence[step][pin])
                time.sleep(0.01) # 10 ms delay
            print(f"Loop {i}")

class Motor:
    
    def __init__ (self, pi, pwm, forwardpin, backwardpin):
        
        self.pi = pi

        # Setting forward and backward control for motor
        self.forwardPin = forwardpin
        self.backwardPin = backwardpin

        # Set motor pins as output
        self.pi.setup(self.forwardPin, self.pi.OUT)
        self.pi.setup(self.backwardPin, self.pi.OUT)
        
        # PWM Setup
        self.pwmpin = pwm
        self.pi.setup(self.pwmpin, self.pi.OUT)
        self.pwm = self.pi.PWM(self.pwmpin, 17500)
        self.pwm.start(0)
        self.set_speed(0)

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
    
    def set_speed(self, dc):
        """Sets duty cycle of PWM to amount between 0 and 100"""
        self.pwm.ChangeDutyCycle(dc)
        return


#TESTING CODE
#GPIO.setmode(GPIO.BOARD)
#GPIO.setwarnings(False)

#stepper = Stepper(GPIO, 8, 10, 35, 16)
#stepper.clockwise(2048)
#time.sleep(2)
"""
motor1 = Motor(GPIO, 32, 40, 37)
motor2 = Motor(GPIO, 12, 13, 15)
controller = MotorController(GPIO, 36, [motor1, motor2])
motor1.set_speed(4)
motor2.set_speed(11.25)
#motor1.setBackward()
#motor2.setBackward()
motor1.stop()
motor2.stop()

while True:
    try:
        controller.turn_cw()
        time.sleep(10)
    except KeyboardInterrupt:
        controller.stop()
        controller.cleanup()
        #motor1.stop()
        #motor2.stop()
        #GPIO.cleanup()
"""