import mfrc522
from time import sleep
import RPi.GPIO as GPIO

class rfid_scanner():

    def __init__ (self):
        self.reader = mfrc522.MFRC522()

    def read_data(self):
        """Start reading sequence, return when data read."""
        while True:

            # Scan for cards
            (status,TagType) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)

            # Get the UID of the card
            (status,uid) = self.reader.MFRC522_Anticoll()

            # If we have the UID, continue
            if status == self.reader.MI_OK:

                # Print UID
                print("UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))

                # Return letter of sticker by comparing 3rd number of UID with database
                return self.uid_to_sticker(uid[2])
    
    def uid_to_sticker(self, data):
        """Converts UID data to sticker letter from database, if it exists. Otherwise, returns None"""
        if data == 241:
            return "a"
        elif data == 237:
            return "b"
        elif data == 232:
            return "c"
        elif data == 228:
            return "d"
        elif data == 224:
            return "e"
        elif data == 220:
            return "f"
        elif data == 216:
            return "g"
        elif data == 212:
            return "h"
        elif data == 208:
            return "i"
        elif data == 204:
            return "j"
        else:
            return None
