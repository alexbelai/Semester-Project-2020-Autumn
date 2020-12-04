# Main robot control file
import speech
import deepspeech                           # Machine learning model library
import numpy as np                          # Numpy for audio buffer data arrays
#import motors
from subprocess import call                 # Send commands to Pi. Mostly used to program shutdown button.
from time import sleep                      # Delay function
#import sensor
#import pigpio                               # Raspberry Pi Pin control
import os                                   # Get path function
from halo import Halo                       # Animated spinners for loading
from time import perf_counter as timer   # Timer to time model load speed
from threading import Thread


# TODO: Transfer to normal pbmm deepspeech model compatible with Pi
# TODO: Implement Spinner to recognizing audio


# Pin Definitions

# Initialize motors
# motor1 = motors.Motor(0,0) # Left
# motor2 = motors.Motor(0,0) # Right
# motorGroup = [motor1, motor2]

# Initialize motor controller
# motorControl = motors.MotorController(motorGroup)

def main():
    # TODO: Reset pins at shutdown

    # Initialize Thread 1 as speech recognition running in background. Note: Thread is a subclass of Recognizer
    thread1 = speech.Recognizer(print_result, print_intent)

    # Initialize Thread 2 as whatever else function or class
    #stop_thread = False
    #thread2 = Thread(target = test_thread, args = (lambda : stop_thread, )) # stop_thread is turned into a function that is checked each time
    
    # Start both threads
    thread1.start()
    #thread2.start()
    print("Successfully started threads")

    # Main Loop, exiting on Ctrl-C
    while True:
        try:
            print("Running...")
            sleep(1)
        except KeyboardInterrupt:
            print("Closing threads...")
            #stop_thread = True # Stops infinite loop in function thread 2
            thread1.terminate() # Stops infinite loop in class thread 1
            thread1.join() # Joins closed thread1 with main loop
            #thread2.join() # Joins closed thread2 with main loop
            break
    #print(thread1.is_alive(), thread2.is_alive()) # Debugging purposes to check if threads killed correctly
    print("Exiting program")

def print_intent(intent):
    """
    This is the function which can extract speech-to-intent data from Rhino. It is called with an object with "is_understood", "intent" and "slots" getters.
    """
    if intent.is_understood:
        print("Understood intent: {}".format(intent.intent))
        for slot, value in intent.slots.items():
            print("    {} : {}".format(slot, value))
    else:
        print("Didn't understand the command.")

def print_result(result):
    """
    This is the function which can extract data from the DeepSpeech engine. It will be called with a string every time something is transcribed by the robot.
    """
    print ("Recognized: {}".format(result))
    return

def test_thread(stop):
    """
    Function to test thread usage, infinite while loop
    """
    while True:
        print("holy shit this works")
        sleep(1)
        if stop():
            break

#def shutdown():
#    """Shut down system by passing a commmand to commmand line."""
#
#    call(["sudo", "shutdown", "-h", "now"]) # "Sudo" for admin rights, "-h" for halting after shutting down processes


if __name__ == "__main__":
    main()
