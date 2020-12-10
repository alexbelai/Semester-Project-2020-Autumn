from threading import Thread
from queue import Queue
from time import sleep
from motors import *

class Movement(Thread):
    """
    Class holding majority of movement and motor controls, its main task is to interpret commands from speech queue.
    """
    def __init__(self, queue, pi, map):

        # Multithreading
        super(Movement, self).__init__()

        self.map = map
        self.queue = queue
        self.motor1 = Motor(pi, 0, 0) # Motor 1, requires 2 pins as input
        self.motor2 = Motor(pi, 0, 0) # Motor 2, requires 2 pins as input
        self.dcmotors = MotorController(pi, [self.motor1, self.motor2])
        self.stepper = Stepper(pi, 0, 0, 0, 0) # Stepper motor, requires 4 pins as input

    def run(self):
        """
        Called on startup of thread class, constantly runs in background.
        """
        while True:

            # Check if data in queue
            data = self.check_for_commands()
            if data is not None:

                # Split commands into a list of two elements. First element is command itself, second element is argument to execute command with.
                commands = data.split()

                # Stepper Pill Mechanism
                if commands[0] == "pill":

                    amount = int(commands[1])
                    thread3 = Thread(target = self.stepper.clockwise, args = (amount))
                    # TODO: RAISE ARM WITH PILLS
                    thread3.join()

                # Move to Specific Table
                elif commands[0] == "navigate":
                    thread4 = Thread(target = self.map.print)
                    thread4.join()
                    # TODO: IMPLEMENT NAVIGATION CODE

                self.queue.task_done() # Indicate that task has been processed
            else:
                sleep(0.01)

    def check_for_commands(self):
        """
        Function checks whether there are any speech commands in queue. Returns the command if there are, returns None if there aren't.
        """
        try:
            data = self.queue.get(block = False)
            return data
        except:
            return None