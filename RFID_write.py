
import pigpio
import time

from mfrc522 import SimpleMFRC522

writter = SimpleMFRC522()

try:
    new_info = input("New info:")
    print("Place the tag, to write")
    writter.write(new_info)
    print("new info saved")