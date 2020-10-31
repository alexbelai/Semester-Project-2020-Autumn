import motors
from subprocess import call # Library to send commands to Pi. Mostly used to program shutdown button.
import gpiozero # Library for pin inputs/outputs on the board
from time import sleep # Delay function

# Pin Definitions

shutdown_button = gpiozero.Button(17, hold_time=2) # Have to hold it for 2 seconds to activate

def main():
    while True:
        shutdown_button.when_held = shutdown


def shutdown():
    """
    Shut down system by passing a commmand to commmand line.
    """
    call(["sudo", "shutdown", "-h", "now"]) # "Sudo" for admin rights, "-h" for halting after shutting down processes

if __name__ == "__main__":
    main()
