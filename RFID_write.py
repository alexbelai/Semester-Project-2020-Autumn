from mfrc522 import SimpleMFRC522

class RFID_write():
    def __init__(self):
        writter = SimpleMFRC522()

def write(self, info):
    try:
        print("Place the tag, to write")
        self.writter.write(info)
        print("new info saved")