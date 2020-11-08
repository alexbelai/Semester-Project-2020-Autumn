# Main robot control file

from pathlib import Path
import speech
import deepspeech
import motors
from subprocess import call # Library to send commands to Pi. Mostly used to program shutdown button.
import gpiozero # Library for pin inputs/outputs on the board
from time import sleep # Delay function
import sensor

# Pin Definitions
shutdown_button = gpiozero.Button(0, hold_time=2) # Have to hold it for 2 seconds to activate
speech_button = gpiozero.Button(0)

# Initialize motors
motor1 = motors.Motor(0,0) # Left
motor2 = motors.Motor(0,0) # Right
motorGroup = [motor1, motor2]


Sensor = sensor.UltrasonicSensor(0,1)

# Initialize motor controller
motorControl = motors.MotorController(motorGroup)

# Create deepspeech model
modelPath = str(Path().absolute()/'model'/'deepspeech-0.8.2-models.tflite') # TODO: Transfer to normal pbmm model compaible with Pi
ds = deepspeech.Model(modelPath)


def main():
    while True:
        shutdown_button.when_held = shutdown

        # TODO: Reset pins at shutdown


def shutdown():
    """Shut down system by passing a commmand to commmand line."""

    call(["sudo", "shutdown", "-h", "now"]) # "Sudo" for admin rights, "-h" for halting after shutting down processes

if __name__ == "__main__":
    main()
