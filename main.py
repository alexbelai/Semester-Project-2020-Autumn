# Main robot control file
import speech
import rfid
import deepspeech                           # Machine learning model library
import numpy as np                          # Numpy for audio buffer data arrays
import motors_GPIO
from subprocess import call                 # Send commands to Pi. Mostly used to program shutdown button.
from time import sleep                      # Delay function
import sensor
import RPi.GPIO as GPIO
import os                                   # Get path function
from halo import Halo                       # Animated spinners for loading
from time import perf_counter as timer      # Timer to time model load speed
from threading import Thread                # Multithreading
from queue import Queue                     # Queue module, used to pass information between threads in a shared queue
import movement
import mapping

def main():

    pi = GPIO # Sets current Pi as controlled Pi
    GPIO.setmode(GPIO.BOARD)#sets GPIO mode to board, so that pins can be called by their numbers

    # Initialize queue to put speech commands in
    speechqueue = Queue()

    # Initialize Thread 1 as speech recognition running in background. 
    thread1 = speech.Recognizer(speechqueue)

    # Initialize Thread 2 as movement class, checking queue for commands.
    thread2 = movement.Movement(speechqueue, pi, "map1.txt", "l", (2,5))

    # Initialize Thread 2 as whatever else function or class
    #stop_thread = False
    #thread2 = Thread(target = test_thread, args = (lambda : stop_thread, )) # stop_thread is turned into a function that is checked each time
    
    # Start both threads
    thread1.start()
    thread2.start()
    print("Successfully started threads")

    # Main Loop, exiting on Ctrl-C
    while True:
        try:
            print("Running...")
            sleep(1)
        except KeyboardInterrupt:
            print("Closing threads...")

            # Stop thread1
            thread1.terminate()
            thread1.join() 

            # Stop thread2
            thread2.stop()
            thread2.join()

            # Release GPIO resources
            #GPIO.cleanup()
            break

    print("Exiting program")

#def shutdown():
#    """Shut down system by passing a commmand to commmand line."""
#
#    call(["sudo", "shutdown", "-h", "now"]) # "Sudo" for admin rights, "-h" for halting after shutting down processes


if __name__ == "__main__":
    main()
