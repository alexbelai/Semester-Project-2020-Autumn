import MFRC522
from time import sleep
import RPi.GPIO as GPIO

"""
class rfid_scanner():

   def _init_(self):
    self.rfid = SimpleMFRC522()

    def read(self): 
        while True:
            id, info = self.rfid.read()
            print(id)
            print(info)
            sleep(1)


    def write(self, info):
        print("Place the tag, to write")
        self.rfid.write(info)
        print("new info saved")
"""
class rfid_scanner():

    def __init__ (self):
        self.reader = MFRC522.MFRC522()

    def read_data(self):

        while True:

            # Scan for cards
            (status,TagType) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)

            # Get the UID of the card
            (status,uid) = self.reader.MFRC522_Anticoll()

            # If we have the UID, continue
            if status == self.reader.MI_OK:
                # Print UID
                print("UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))
                time.sleep(2)
