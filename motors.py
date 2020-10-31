import pigpio
pi = pigpio.pi() # Sets current Pi as controlled Pi

class MotorController():

    def __init__ (self, motors):

        # Extract motors from list
        self.motors = motors
        self.frontLeft = self.motors[0]
        self.frontRight = self.motors[1]
        self.backLeft = self.motors[2]
        self.backRight = self.motors[3]

        # Set up HBridge pins for Motors
        self.HBEnable12 = 0
        self.HBEnable34 = 0
        pi.set_mode(self.HBEnable12, pigpio.OUTPUT)
        pi.set_mode(self.HBEnable34, pigpio.OUTPUT)
        pi.write(self.HBEnable12, 1)
        pi.write(self.HBEnable34, 1)
    
    def forward(self):
        """
        Sets all motors to move forward
        """
        for motor in self.motors:
            motor.setForward()

    def backward(self):
        """
        Sets all motors to move backward
        """
        for motor in self.motors:
            motor.setBackward()
    
    def right(self):
        """
        Turns right
        """
        self.frontLeft.stop()
        self.backLeft.stop()
        self.frontRight.setForward()
        self.backRight.setForward()

    def left(self):
        """
        Turns right
        """
        self.frontLeft.setForward()
        self.backLeft.setForward()
        self.frontRight.stop()
        self.backRight.stop()


class Motor():
    
    def __init__ (self, forwardpin, backwardpin):
        
        # Setting forward and backward control for motor
        self.forwardPin = forwardpin
        self.backwardPin = backwardpin

        # Set motor pins as output
        pi.set_mode(self.forwardPin, pigpio.OUTPUT)
        pi.set_mode(self.backwardPin, pigpio.OUTPUT)

        # Clear motor pins on init
        self.stop()

    def getCurrentState(self):
        """
        Returns current state of motor pins in a tuple of 0s or 1s (forwardstate, backwardstate)
        """
        return (pi.read(self.forwardPin), pi.read(self.backwardPin))

    def setForward(self):
        """
        Set forward pin of motor while turning off other pin
        """
        pi.write(self.forwardPin, 1)
        pi.write(self.backwardPin, 0)

    def setBackward(self):
        """
        Set forward pin of motor while turning off other pin
        """
        pi.write(self.backwardPin, 1)
        pi.write(self.forwardPin, 0)

    def stop(self):
        """
        Stops the given motor by clearing pins
        """
        pi.write(self.forwardPin, 0)
        pi.write(self.backwardPin, 0)
