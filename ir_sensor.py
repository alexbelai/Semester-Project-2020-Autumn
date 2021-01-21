# IR sesnors : These sensors have an infrared (IR) receiver and transmitter.
#  Black things (e.g. black electrical tape) absorb IR light;
#  White things (e.g. white poster board) reflect IR light.
#  Hence while black, in = LOW
import time
from threading import Thread
from time import sleep
import RPi.GPIO as GPIO

class IRSensor():

    def __init__(self, pi, in_pin):
        self.pi = pi
        self.in_pin = in_pin
        self.pi.setup(self.in_pin, self.pi.IN)

    def scan_line(self):
        """Read data using sensor. Returns True if no signal, False if signal."""
        data = self.pi.input(self.in_pin)
        if data == 1:
            return True
        elif data == 0:
            return False

class IRController(Thread):

    def __init__(self, pi, queue, inpin1, inpin2):

        super(IRController, self).__init__()
        
        self.pi = pi
        self.queue = queue
        self.running = True
        self.sensor1 = IRSensor(pi, inpin1)
        self.sensor2 = IRSensor(pi, inpin2)

    def run(self):
        """Called on thread startup"""
        while self.running:

            data1 = self.sensor1.scan_line()
            data2 = self.sensor2.scan_line()

            if data1 == True and data2 == True:

                #Both sensors on line, go forward
                #self.queue.put("f")
                print("forward")
                    
            elif data1 == True and data2 == False:
                #Turn left
                self.queue.put("l")
                print("left")

            elif data1 == False and data2 == True:
                self.queue.put("r")
                print("right")
                
            elif data1 == False and data2 == False:
                self.queue.put("b")
                print("back")
            
            sleep(0.2)

    def stop(self):
            """Stops sensing and autocorrection"""
            self.running = False

#TESTING CODE
#GPIO.setmode(GPIO.BOARD)
#GPIO.setwarnings(False)
#sensors = IRController(GPIO, 29, 31)
#sensors.start()
#while True:
#   sleep(1)