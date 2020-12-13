# IR sesnors : These sensors have an infrared (IR) receiver and transmitter.
#  Black things (e.g. black electrical tape) absorb IR light;
#  White things (e.g. white poster board) reflect IR light.
#  Hence while black, in = LOW
import pigpio
import time

pi = pigpio.pi()

class IRSensor():
    def __init__(self, in_pin):
        self.in_pin = in_pin
        pi.set_mode(self.in_pin, pigpio.INPUT)
        pi.write(self.in_pin, 0)


    def scan_line(self):
        if self.in_pin.read() == 1:
            return True
        elif self.in_pin.read() == 0:
            return False
