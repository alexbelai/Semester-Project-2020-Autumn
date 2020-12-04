from mfrc522 import SimpleMFRC522


class RFID_read():
   def _init_(self):
    self.reader = SimpleMFRC522()

def Read_tag(self): 
    try:
        id, info = self.reader.read()
        print(id)
        print(info)