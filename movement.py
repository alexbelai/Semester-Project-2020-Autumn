from threading import Thread
from queue import Queue
from time import sleep
from motors import *
from mapping import *

class Movement(Thread):
    """
    Class holding majority of movement and motor controls, its main task is to interpret commands from speech queue.

    :param queue: Queue between threads to which the speech engine adds commands
    :param pi: Instance of Raspberri Pi GPIO object used to write and read pins
    :param mapfile: A text file containing the imaginary map that the robot navigates
    :param startcoords: Starting position of the robot on the given mapfile with the formula (y, x)
    """
    def __init__(self, queue, pi, mapfile, startcoords):

        # Multithreading
        super(Movement, self).__init__()

        self.map = Map(mapfile, startcoords)
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
                if commands[0] == "pillCount":

                    amount = int(commands[1])
                    thread3 = Thread(target = self.stepper.clockwise, args = (amount))
                    # TODO: RAISE ARM WITH PILLS
                    thread3.join()

                # Move to Specific Table
                elif commands[0] == "tableName":
                    table = commands[1] # Stores letter of table ranging from "a" to "d"
                    path = self.map.find_path(table)
                    print(path)
                    # TODO: IMPLEMENT MOVEMENT CODE BASED ON PATH GIVEN

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

    def number_of_pills(self, number):
        """Converts commands from Speech-To-Intent engine to integrers."""
        if number == "one":
            return 1
        elif number == "two":
            return 2
        elif number == "three":
            return 3
        elif number == "four":
            return 4
        elif number == "five":
            return 5
        elif number == "six":
            return 6