import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False )
GPIO.setmode(GPIO.BOARD)

#TODO implement all 3 sensor readings as an object

class UltrasonicSensor():
    def __init__(self, echo_pin, trig_pin):

            self.echo_pin = echo_pin
            self.trig_pin = trig_pin

            # Set Pins to Inputs or Outputs

            GPIO.setup(trig_pin, GPIO.OUT)
            GPIO.setup(echo_pin, GPIO.IN)

            GPIO.output(trig_pin, 0)
            time.sleep(0.2)
    
    def read_Distance(self):
        GPIO.output(self.trig_pin, 1)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, 0)

        while GPIO.input(self.echo_pin) == 0:
            pass
        pulse_start = time.time()

        while GPIO.input(self.echo_pin) == 1:
            pass
        pulse_stop = time.time()

        distance = round(((pulse_stop - pulse_start) * 17000), 2)  # distance in cm
        time.sleep(0.2)

        return distance
