from threading import Thread
from queue import Queue
from time import sleep
from motors_GPIO import *
from mapping import *
from ir_sensor import *
from rfid import *
from servo import *

class Movement(Thread):
    """
    Class holding majority of movement and motor controls, its main task is to interpret commands from speech queue.

    :param queue: Queue between threads to which the speech engine adds commands
    :param pi: Instance of Raspberri Pi GPIO object used to write and read pins
    :param mapfile: A text file containing the imaginary map that the robot navigates
    :param startcoords: Starting position of the robot on the given mapfile with the formula (y, x)
    """
    def __init__(self, queue, pi, mapfile, startdirect, startcoords):

        # Multithreading
        super(Movement, self).__init__()

        self.pi = pi
        self.map = Map(mapfile, startcoords)
        self.queue = queue
        self.running = True
        self.direction = startdirect
        self.motor1 = Motor(self.pi, 32, 40, 37) # Motor 1, requires 2 pins as input
        self.motor2 = Motor(self.pi, 12, 13, 15) # Motor 2, requires 2 pins as input
        self.motors = MotorController(self.pi, 36, [self.motor1, self.motor2])
        self.servo = ServoController(GPIO, 11)
        self.stepper = Stepper(self.pi, 8, 10, 35, 16) # Stepper motor, requires 4 pins as input
        self.motors.stop()
        
    def run(self):
        """
        Called on startup of thread class, constantly runs in background.
        """
        while self.running:

            if self.queue.empty():

                sleep(0.1)

            else:  
                
                # Get commands as list of two elements. First element is command itself, second element is argument to execute command with.
                data = self.queue.get()
                print(f"Got command {data}")

                # Stepper Pill Mechanism
                if data[0] == "pillCount":
                    
                    # 528 is a full loop, 132 is 90 degrees of rotation = 1 pill
                    amount = 132 * self.number_of_pills(data[1])
                    self.stepper.clockwise(amount)
                    time.sleep(2)
                    print("Raising arm...")
                    self.servo.arm_up()
                    time.sleep(2)
                    self.servo.arm_down()
                    print("----------------------------------------")
                    print("DONE")
                    print("----------------------------------------")

                # Move to Specific Table
                elif data[0] == "tableName":
                    table = data[1] # Stores letter of table ranging from "a" to "d"
                    path = self.map.find_path(table)
                    print(path)
                    self.move_on_path(path)
                    print("----------------------------------------")
                    print("DONE")
                    print("----------------------------------------")

                    """
                    explored_stickers = set()
                    explored_stickers.add("e")
                    rfidqueue = Queue()
                    rfidthread = rfid_scanner(rfidqueue)
                    rfidthread.start()
                    irqueue = Queue()
                    irthread = IRController(self.pi, irqueue, 29, 31)
                    irthread.start()
                    self.motors.forward()
                    jaquan = True
                    first = True
                    while jaquan:
                        if rfidqueue.empty():
                            
                            if irqueue.empty():
                                time.sleep(0.01)
                            
                            else:
                                self.motors.stop()                            
                                data = irqueue.get()    
                            
                                # If have to move a bit left to correct reading
                                if data == "l":
                                    
                                    # Stop motors, turn left
                                    self.motors.bit_left()
                                    
                                    # Stop thread
                                    print("Stopping thread")
                                    irthread.stop()
                                    irqueue.task_done()
                                    irthread.join()
                                    print("Stopped thread")
                                    
                                    # Start thread again
                                    irqueue = Queue()
                                    irthread = IRController(self.pi, irqueue, 29, 31)
                                    irthread.start()
                                    print("Started thread")
                                    self.motors.forward()
                                    time.sleep(0.2)

                                # If have to move a bit right to correct reading
                                elif data == "r":
                                    self.motors.bit_right()
                                    print("Stopping thread")
                                    irthread.stop()
                                    irqueue.task_done()
                                    irthread.join()
                                    print("Stopped thread")
                                    irqueue = Queue()
                                    irthread = IRController(self.pi, irqueue, 29, 31)
                                    irthread.start()
                                    print("Started thread")
                                    self.motors.forward()
                                    time.sleep(0.2)
                                    
                                elif data == "b":
                                    
                                    # Stop motors, turn left
                                    self.motors.backward()
                                    time.sleep(1)
                                    self.motors.stop()
                                    
                                    # Stop thread
                                    print("Stopping thread")
                                    irthread.stop()
                                    irqueue.task_done()
                                    irthread.join()
                                    print("Stopped thread")
                                    
                                    # Start thread again
                                    irqueue = Queue()
                                    irthread = IRController(self.pi, irqueue, 29, 31)
                                    irthread.start()
                                    print("Started thread")
                                    self.motors.forward()
                                    time.sleep(0.2)
                        else:
                            data = rfidqueue.get()
                            print(data)
                            rfidqueue.task_done()
                            
                            if data not in explored_stickers:
                                self.motors.stop()
                                rfidthread.stop()
                                rfidthread.join()
                                irthread.stop()
                                irthread.join()
                                explored_stickers.add(data)
                                if first:
                                    self.motors.turn_ccw()
                                    first = False
                                else:
                                    self.motors.turn_cw()
                                irqueue = Queue()
                                irthread = IRController(self.pi, irqueue, 29, 31)
                                irthread.start()
                                self.motors.forward()
                                rfidqueue = Queue()
                                rfidthread = rfid_scanner(rfidqueue)
                                rfidthread.start()
                            else:
                                continue
                        """
                            
                self.queue.task_done() # Indicate that task has been processed

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

    def stop(self):
        """Stops thread listening for commands."""
        self.running = False
    
    def move_on_path(self, path):
        """Executes each command in a list of elements to navigate on map."""

        # Repeat until last destination left
        while len(path) > 1 and self.running:

            # Unpack commands, set current coords
            current = path[0]
            path = path[1:]
            coords, direct = current
            self.map.set_current_coords(coords)
            print(current)

            # Initialize queue for communication with IR and RFID Thread
            irqueue = Queue()
            rfidqueue = Queue()
            
            # If no orientation change required
            if self.direction == direct:
                self.motors.forward()

            # If you have to turn for next command
            else:
                self.motors.turn(self.direction, direct)
                self.direction == direct
                self.motors.forward()

            # Start threads
            irthread = IRController(self.pi, irqueue, 29, 31)
            rfidthread = rfid_scanner(rfidqueue)
            irthread.start()
            rfidthread.start()

            # Repeat until you are at an RFID junction
            junction = False
            while junction == False:

                if rfidqueue.empty():
                    
                    if irqueue.empty():
                        time.sleep(0.01)
                    
                    else:
                        self.motors.stop()                            
                        data = irqueue.get()    
                    
                        # If have to move a bit left to correct reading
                        if data == "l":
                            
                            # Stop motors, turn left
                            self.motors.bit_left()
                            
                            # Stop thread
                            irthread.stop()
                            irqueue.task_done()
                            irthread.join()
                            
                            # Start thread again
                            irqueue = Queue()
                            irthread = IRController(self.pi, irqueue, 29, 31)
                            irthread.start()
                            self.motors.forward()
                            time.sleep(0.1)

                        # If have to move a bit right to correct reading
                        elif data == "r":
                            self.motors.bit_right()

                            irthread.stop()
                            irqueue.task_done()
                            irthread.join()

                            irqueue = Queue()
                            irthread = IRController(self.pi, irqueue, 29, 31)
                            irthread.start()

                            self.motors.forward()
                            time.sleep(0.1)
                            
                        elif data == "b":
                            
                            self.motors.backward()
                            time.sleep(0.75)
                            self.motors.stop()
                            
                            irthread.stop()
                            irqueue.task_done()
                            irthread.join()
                            
                            irqueue = Queue()
                            irthread = IRController(self.pi, irqueue, 29, 31)
                            irthread.start()

                            self.motors.forward()
                            time.sleep(0.1)

                else:

                    # Stop motors and threads, reset IRQueue
                    self.motors.stop()
                    rfidthread.stop()
                    irthread.stop()
                    rfidthread.join()
                    irthread.join()

                    # Read letter of sticker encountered and get coordinates of it
                    data = rfidqueue.get()
                    print(data)
                    readsticker = self.map.get_coords_of_sticker(data)

                    # Find coordinate in list of commands and set current coords to it
                    for i in range(len(path)):
                        if path[i][0] == readsticker:
                            self.map.set_current_coords(readsticker)
                            index = i
                            break
                    
                    path = path[(index + 1):]
                    rfidqueue.task_done()
                    junction = True