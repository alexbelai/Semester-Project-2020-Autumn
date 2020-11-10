# Main robot control file
# Parts of code based on the following blogs, tutorials, and codes:
#
#       Sparkfun
#       https://learn.sparkfun.com/tutorials/raspberry-pi-safe-reboot-and-shutdown-button/all

from pathlib import Path
import deepspeech
import motors
from subprocess import call # Library to send commands to Pi. Mostly used to program shutdown button.
import gpiozero # Library for pin inputs/outputs on the board
from time import sleep # Delay function

# Pin Definitions
shutdown_button = gpiozero.Button(0, hold_time=2) # Have to hold it for 2 seconds to activate
speech_button = gpiozero.Button(0)

# Initialize motors
motor1 = motors.Motor(0,0) # Front Left
motor2 = motors.Motor(0,0) # Front Right
motor3 = motors.Motor(0,0) # Back Left
motor4 = motors.Motor(0,0) # Back Right
motorGroup = [motor1, motor2, motor3, motor4]

# Initialize motor controller
motorControl = motors.MotorController(motorGroup)

# Create deepspeech model
modelPath = str(Path().absolute()/'model'/'deepspeech-0.8.2-models.tflite') # TODO: Transfer to normal pbmm model compaible with Pi
speech = deepspeech.Model(modelPath)


def main():
    while True:
        shutdown_button.when_held = shutdown

        # TODO: Reset pins at shutdown


def shutdown():
    """
    Shut down system by passing a commmand to commmand line.
    """
    call(["sudo", "shutdown", "-h", "now"]) # "Sudo" for admin rights, "-h" for halting after shutting down processes

if __name__ == "__main__":
    main()