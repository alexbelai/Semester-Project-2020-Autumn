import deepspeech
import numpy as np
import pyaudio
import time
import webrtcvad
import queue
import collections
from threading import Thread
import os
from time import perf_counter as timer      # Timer to time model load speed
from halo import Halo                       # Animated spinners for loading
from pvporcupine import Porcupine           # Porcupine



# Global Variables
FORMAT = pyaudio.paInt16 # 16-bit format required by WebRTCVad
INPUTRATE = 16000 # Sampling rate = 16kHZ
CHANNELS = 1 # Mono audio required by WebRTCVad
BLOCKS_PER_SECOND = 50 # 50 blocks of audio generated per second

# TODO: Create start stream functionality in "Audio" class
# TODO: Implement Resample
# TODO: Add print statements to initialization to log what's happening

class Audio:
    """Class holding PyAudio objects"""
    def __init__ (self):

        self.buffer = queue.Queue() # Initiate queue to put audio segments in
        self.block_size = int(INPUTRATE / float(BLOCKS_PER_SECOND)) # Determine size of audio blocks
        self.frame_duration_ms = 1000 * self.block_size // INPUTRATE # Duration of one block of audio in ms

        # Initiate PyAudio
        self.pa = pyaudio.PyAudio() 

        # Callback function for PyAudio (whenever called, add data to queue)
        def thread_callback(in_data, frame_count, time_info, status):
            self.buffer.put(in_data)
            return(None, pyaudio.paContinue)

        # Open Stream
        self.stream = self.pa.open(
            format = FORMAT,
            channels = CHANNELS,
            rate = INPUTRATE,
            input = True, # Specify as input
            frames_per_buffer= self.block_size,
            stream_callback = thread_callback
        )
        self.stream.start_stream()

    def close(self):
        """Shut down PyAudio voice recognition."""
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
    
    def read(self):
        """Return a block of audio data from queue"""
        return self.buffer.get()

class VoiceActivityDetector(Audio):
    """Class holding WebRTC VAD implementation, detecting voice activity and feeding it to DeepSpeech"""

    def __init__(self, aggressiveness):
        self.vad = webrtcvad.Vad(aggressiveness)
        super().__init__()

    def frame_generator(self):
        """Generator that yields audio frames from microphone"""
        while True:
            yield self.read()

    def vad_collector(self, padding_ms = 300, ratio = 0.75):
        """
        Generator that yields series of audio segments with "None" between them by iterating a "sliding window" over audio.

        padding_ms is the window observed around the audio (Default: 300ms)

        ratio is the ratio of audio frames required in the padding zone for the VAD to trigger (Default: 75%)
        """
        frames = self.frame_generator() # Extracting frames from audio
        num_padding_frames = int(padding_ms / self.frame_duration_ms) # Number of padding frames based on ms given (default: 6)
        ring_buffer = collections.deque(maxlen=num_padding_frames) # List-like sequence with fast access at endpoints, used for sliding window

        # Generator has two states: TRIGGERED and NOT TRIGGERED, initiallly we set it to not triggered.
        triggered = False

        for frame in frames:

            # Extra line of code contained in model example, discard small samples?
            #if len(frame) < 640:
            #    return

            is_speech = self.vad.is_speech(frame, INPUTRATE) # check whether given frame is a speech frame or not

            if not triggered: # NOT TRIGGERED State
                ring_buffer.append((frame, is_speech)) # add frame to queue as (data,False)
                num_voiced = len([f for f, speech in ring_buffer if speech]) # sum up number of speech frames in queue

                # If VAD in NOT TRIGGERED state and more than "ratio"% of frames in ring buffer are voiced, enter TRIGGERED state
                if num_voiced > ratio * ring_buffer.maxlen:
                    triggered = True

                    # Start yielding audio by yielding the frames already in queue
                    for f, s in ring_buffer:
                        yield f
                    ring_buffer.clear()

            else: # TRIGGERED State
                yield frame
                ring_buffer.append((frame, is_speech)) # add frame to queue as (data,True)
                num_unvoiced = len([f for f, speech in ring_buffer if not speech]) # sum up number of non-speech frames in queue

                # If VAD in TRIGGERED state and more than "ratio"% of frames in ring buffer are non-voiced, enter NOT TRIGGERED state
                if num_unvoiced > ratio * ring_buffer.maxlen:
                    triggered = False

                    # Stop yielding audio
                    yield None
                    ring_buffer.clear()

class Recognizer(Thread):
    """
    Class for wake word detection using Porcupine, PyAudio, WebRTCVad and DeepSpeech library. 
    It creates an input audio stream, which it monitors on a separate thread for a wake word.
    Whenever the wake word is heard, it starts transcribing audio until word "stop" is mentioned.
    """
    def __init__(self,
        dsname,
        library_path,
        model_path,
        keyword_paths,
        sensitivities,
        dsscorername = None,
        use_scorer = False,
        aggressiveness = 0,):

        # Multithreading
        super(Recognizer, self).__init__()

        # Init variables
        self.dsname = dsname
        self.dsscorername = dsscorername
        self.use_scorer = use_scorer
        self.aggressiveness = aggressiveness
        self.library_path = library_path
        self.model_path = model_path
        self.keyword_paths = keyword_paths
        self.sensitivities = sensitivities

        # Initialize DeepSpeech model
        modelPath = str(os.path.join(os.getcwd(), "model", self.dsname))
        print("Trying to open model at {}".format(modelPath))
        modelLoadStart = timer()
        self.ds = deepspeech.Model(modelPath)
        modelLoadEnd = timer()
        print("Successfully loaded model in {:.3}s".format(modelLoadEnd - modelLoadStart))

        # Initialize scorer
        if self.use_scorer:
            scorerPath = str(os.path.join(os.getcwd(), "model", self.dsscorername))
            if os.path.exists(scorerPath):
                scorerLoadStart = timer()
                self.ds.enableExternalScorer(modelPath)
                scorerLoadEnd = timer()
                print("Successfully loaded scorer in {:.3}s".format(scorerLoadEnd - scorerLoadStart))
    
    def transcribe(self):
        """
        Initialize voice activity detection and feed it to DeepSpeech model to transcribe.
        """

        # Initialize voice activity detector and audio stream with agressiveness between 0 and 3
        vad_audio = VoiceActivityDetector(self.aggressiveness)
        print("Listening to input (ctrl-C to exit)")
        frames = vad_audio.vad_collector()

        try:
            # Init loading bar and stream
            spinner = Halo(spinner = 'line', color = 'magenta')
            modelStream = self.ds.createStream()
            
            for frame in frames:

                # If encountering a non-empty frame, feed it to model and start loading
                if frame is not None:
                    spinner.start()
                    modelStream.feedAudioContent(np.frombuffer(frame, np.int16))

                # If encountering an empty frame, stop feeding to model and print
                else:
                    spinner.stop()
                    text = modelStream.finishStream()
                    print("Recognized: {}".format(text))

                    # If "stop" encountered, stop stream
                    if "stop" in text:
                        vad_audio.close()
                        return 1

                    # Restart Stream
                    modelStream = self.ds.createStream()

        # If interrupted with Ctrl+C, stop recording and close stream
        except KeyboardInterrupt:
            print("Stopping recording")
        finally:
            vad_audio.close()

    def run(self):
        """
        Creates
        """
        
        porcupine = Porcupine(
            library_path = self.library_path,
            model_path = self.model_path,
            keyword_paths = self.keyword_paths,
            sensitivities = self.sensitivities)
            