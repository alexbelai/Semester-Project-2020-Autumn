import RPi.GPIO as GPIO
from threading import Thread
import time


class UltrasonicSensor():
    def __init__(self, pi, echo_pin, trig_pin):

            self.pi = pi
            self.echo_pin = echo_pin
            self.trig_pin = trig_pin

            # Set Pins to Inputs or Outputs

            self.pi.setup(self.trig_pin, GPIO.OUTPUT)
            self.pi.setup(self.echo_pin, GPIO.INPUT)

            pi.write(self.trig_pin, 0)
    
    def read_Distance(self):
        """Reads distance and returns it in centimeteres"""

        self.pi.out(self.trig_pin, 1)
        time.sleep(0.00001)
        self.pi.out(self.trig_pin, 0)

        while self.pi.input(self.echo_pin) == 0:
            pass
        pulse_start = time.time()

        while self.pi.input(self.echo_pin) == 1:
            pass
        pulse_stop = time.time()

        distance = round(((pulse_stop - pulse_start) * 17000), 2)  # distance in cm
        
        if distance < 30:
            return distance

        else:
            return None
        

class USController(Thread):
    def __init__(self, pi, trig1,trig2, echo1, echo2):
        super(USController, self).__init__()
        
        self.pi = pi
        self.running = True
        self.sensor1 = UltrasonicSensor(self.pi, trig1, echo1)
        self.sensor2 = UltrasonicSensor(self.pi, trig2, echo2)

    def run(self):
        """ Should probably find a way to eliminate false readings """
        while self.running:

            read1 = self.sensor1.read_Distance()
            read2 = self.sensor2.read_Distance()

            if read1 != None or read2 != None:
                print("stop")
        time.sleep(0.5)

    def stop(self):
        self.running = False