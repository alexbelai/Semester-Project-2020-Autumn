
import pigpio
from mfrc522 import SimpleMFRC522

class RFID_read():
    reader = SimpleMFRC522()

def Read_tag(self)
    try:
        id, info = reader.read()
        print(id)
        print(info)