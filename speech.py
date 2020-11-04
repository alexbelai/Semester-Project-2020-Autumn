import deepspeech
import numpy as np
import pyaudio
import time
import webrtcvad

# Global Variables
FORMAT = pyaudio.paInt16 # 16-bit Format required by WebRTCVad
INPUTRATE = 16000 # Sampling Rate = 16kHZ
CHANNELS = 1 # Mono Audio required by WebRTCVad

# TODO: Multithreading Implementation for Callback In Stream Init
# TODO: Determine Resample function requirement? - probably no

class Audio:
    """Class holding PyAudio objects"""
    def __init__ (self):

        # Initiate PyAudio
        self.pa = pyaudio.PyAudio() 

        # Define Callback function (Constant Data Transfer)
        # TODO: Multithreading Implementation
        def callback(in_data, frame_count, time_info, status):
            return(in_data, pyaudio.paContinue)

        # Open Stream
        self.stream = self.pa.open(
            format = FORMAT,
            channels = CHANNELS,
            rate = INPUTRATE,
            input = True, # Specify as input
            stream_callback = callback
        )
        self.stream.start_stream()

    def close(self):
        """Shut down PyAudio voice recognition."""
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

class VoiceActivityDetector:
    """Class holding WebRTC VAD implementation, detecting voice activity and feeding it to DeepSpeech"""

    def __init__(self, aggressiveness):
        self.vad = webrtcvad.Vad(aggressiveness)
