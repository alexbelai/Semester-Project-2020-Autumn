import pigpio 
import time

pi = pigpio.pi()

class UltrasonicSensor():
    def __init__(self, echo_pin, trig_pin):

            self.echo_pin = echo_pin
            self.trig_pin = trig_pin

            # Set Pins to Inputs or Outputs

            pi.set_mode(self.trig_pin, pigpio.OUTPUT)
            pi.set_mode(self.echo_pin, pigpio.INPUT)

            pi.write(self.trig_pin, 0)
    
    def read_Distance(self):
        """Reads distance and returns it in centimeteres"""

        pi.write(self.trig_pin, 1)
        time.sleep(0.00001)
        pi.write(self.trig_pin, 0)

        while pi.read(self.echo_pin) == 0:
            pass
        pulse_start = time.time()

        while pi.read(self.echo_pin) == 1:
            pass
        pulse_stop = time.time()

        distance = round(((pulse_stop - pulse_start) * 17000), 2)  # distance in cm
        return distance
    
