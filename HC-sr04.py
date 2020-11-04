import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

TRIG1 = 3
TRIG2 = 5
TRIG3 = 7
ECHO1 = 11
ECHO2 = 13
ECHO3 = 15

# Pins are setup, trig is low
GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)

GPIO.setup(TRIG2, GPIO.OUT)
GPIO.setup(ECHO2, GPIO.IN)

GPIO.setup(TRIG3, GPIO.OUT)
GPIO.setup(ECHO3, GPIO.IN)

GPIO.output(TRIG1, 0)
GPIO.output(TRIG2, 0)
GPIO.output(TRIG3, 0)

time.sleep(0.5)

print("Measuring distance...")

# Output pin (Trig) is set to high for 10us, sending out a small pulse
# Input pin (Echo) is waiting for the pulse to come back
while 1:
    print("Sensor1 active...")
    GPIO.output(TRIG1, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG1, 0)

    while GPIO.input(ECHO1) == 0:
        pass
    pulse_start = time.time()

    while GPIO.input(ECHO1) == 1:
        pass
    pulse_stop = time.time()

    distance1 = round(((pulse_stop - pulse_start) * 17000), 2)  # distance in cm
    print("Distance in cm sensor1: " + str(distance1))
    time.sleep(0.2)

    ###############################################

    print("Sensor2 active...")
    GPIO.output(TRIG2, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG2, 0)

    while GPIO.input(ECHO2) == 0:
        pass
    pulse_start = time.time()

    while GPIO.input(ECHO2) == 1:
        pass
    pulse_stop = time.time()

    distance2 = round(((pulse_stop - pulse_start) * 17000), 2)  # distance in cm
    print("Distance in cm sensor1: " + str(distance2))
    time.sleep(0.2)

    ##############################################

    print("Sensor3 active...")
    GPIO.output(TRIG3, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG3, 0)

    while GPIO.input(ECHO3) == 0:
        pass
    pulse_start = time.time()

    while GPIO.input(ECHO3) == 1:
        pass
    pulse_stop = time.time()

    distance3 = round(((pulse_stop - pulse_start) * 17000),2)  # distance in cm
    print("Distance in cm sensor1: " + str(distance3))

    # Delay between next measurement
    time.sleep(0.5)

    ##
    #distance1
    #distance2
    #distance3
