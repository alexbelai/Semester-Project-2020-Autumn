import deepspeech
import numpy as np
import pyaudio


class Audio:
    def __init__ (self):

        # Initiate PyAudio
        self.pa = pyaudio.PyAudio() 

        # Define Callback function (Constant Data Transfer)
        # TODO: Multithreading Implementation
        def callback(in_data, frame_count, time_info, status):
            return(in_data, pyaudio.paContinue)

        # Open Stream
        self.stream = self.pa.open(
            format = pyaudio.paInt16, # Int16 Format required by DS module
            channels = 1,
            rate = 16000, # Sampling Rate = 16kHZ
            input = True, # Specify as input
            stream_callback = callback
        )
        self.stream.start_stream()

    def close(self):
        """Shut down PyAudio voice recognition."""
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
