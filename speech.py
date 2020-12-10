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
import pvporcupine                          # Wake word detection
import pvrhino                              # Speech to intent
import struct                               # Used to unpack PyAudio data from C to Python



# Global Variables
FORMAT = pyaudio.paInt16 # 16-bit format required by WebRTCVad
INPUTRATE = 16000 # Sampling rate = 16kHZ
CHANNELS = 1 # Mono audio required by WebRTCVad
BLOCKS_PER_SECOND = 50 # 50 required for DeepSpeech so it has 320 long frames

# TODO: Implement Resample
# TODO: Option to pick input device by index

class Audio:
    """Class holding PyAudio objects"""
    def __init__ (self):

        self.buffer = queue.Queue() # Initiate queue to put audio segments in
        self.block_size = int(INPUTRATE / float(BLOCKS_PER_SECOND)) # Determine size of audio blocks
        print(self.block_size)
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
    Whenever the wake word is heard, it starts "Speech-To-Intent" module and interprets commands.
    
    :param speechqueue: Queue to put speech commands in for other threads to interpret
    :param dsname: Name of deepspeech model.
    :param dsscorername: Name of deepspeech scorer.
    :param use_scorer: Whether to use scorer or not. Default: False
    :param aggressiveness: Aggressiveness of Voice Activity Detection from 0-3. Default: 0
    :param porc_library_path: Path to porcupine library (lib/raspberry-pi/arm11/libpv_porcupine.so)
    :param porc_model_path: Path to porcupine model (lib/common/porcupine_params.pv)
    :param porc_keywords: Availabe keywords: Americano, Blueberry, Bumblebee, Grapefruit, Grasshopper, Picovoice, Porcupine, Terminator, Trick-Or-Treat
    :param porc_keyword_paths: Inferred from keywords. (resources/keyword_files/...)
    :param porc_sensitivities: Sensitivity to wake word detection between 0 and 1. Default: 0.5
    :param rhino_library_path: Path to rhino library (lib/raspberry-pi/arm11/libpv_rhino.so)
    :param rhino_model_path: Path to rhino model (lib/common/rhino_params.pv)
    :param rhino_context_path: Path to rhino context file. Will be created and customized on online surface, currently using default (resources/contexts/windows/coffee_maker_windows.rhn)
    """
    def __init__(self,
            queue,

            # Deepspeech variables
            dsname = "deepspeech-0.8.2-models.tflite",                                 
            dsscorername = None,
            use_scorer = False,
            aggressiveness = 0,

            # Porcupine variables
            porc_library_path = pvporcupine.LIBRARY_PATH,
            porc_model_path = pvporcupine.MODEL_PATH,
            porc_keywords = ["blueberry"],
            porc_keyword_paths = None,
            porc_sensitivities = None,

            # Rhino variables
            rhino_library_path = pvrhino.LIBRARY_PATH,
            rhino_model_path = pvrhino.MODEL_PATH,
            rhino_context_path = "resources/context/coffee_maker_windows.rhn"
            ):

        # Multithreading
        super(Recognizer, self).__init__()

        # Init variables
        self.queue = queue
        self.dsname = dsname
        self.dsscorername = dsscorername
        self.use_scorer = use_scorer
        self.aggressiveness = aggressiveness
        self.porc_library_path = porc_library_path
        self.porc_model_path = porc_model_path
        self.porc_keyword_paths = porc_keyword_paths
        self.porc_running = True
        self.rhino_library_path = rhino_library_path
        self.rhino_model_path = rhino_model_path
        self.rhino_context_path = rhino_context_path

        if porc_keyword_paths is None:
            self.porc_keyword_paths = [pvporcupine.KEYWORD_PATHS[x] for x in porc_keywords] # Get keyword path from given keywords
        else:
            self.porc_keyword_paths = str(os.path.join(os.getcwd(), porc_keyword_paths))
        
        if porc_sensitivities is None:
            self.porc_sensitivities = [0.5] * len(self.porc_keyword_paths) # Create a list of "0.5" values the length of amount of keywords

        # Initialize DeepSpeech model
        modelPath = str(os.path.join(os.getcwd(), "model", self.dsname))
        print("Trying to open model at {}".format(modelPath))
        modelLoadStart = timer()
        self.ds = deepspeech.Model(modelPath)
        modelLoadEnd = timer()
        print("Successfully loaded model in {:.3}s".format(modelLoadEnd - modelLoadStart))

        # Initialize DeepSpeech scorer
        if self.use_scorer:
            scorerPath = str(os.path.join(os.getcwd(), "model", self.dsscorername))
            if os.path.exists(scorerPath):
                scorerLoadStart = timer()
                self.ds.enableExternalScorer(modelPath)
                scorerLoadEnd = timer()
                print("Successfully loaded scorer in {:.3}s".format(scorerLoadEnd - scorerLoadStart))
    
    def terminate(self):
        """
        Terminates the while loop for wake word detection, thus being able to close the thread.
        """
        self.porc_running = False
        return

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

                # If encountering an empty frame, stop feeding to model and send data to callback function specified in main
                else:
                    spinner.stop()
                    text = modelStream.finishStream()
                    self.print_result(text)
                    return 1
                    # If "stop" encountered, stop stream
                    # if "stop" in text:
                    #    vad_audio.close()
                    #    return 1

                    # Restart Stream
                    # modelStream = self.ds.createStream()

        # If interrupted with Ctrl+C, stop recording and close stream
        except KeyboardInterrupt:
            print("Stopping recording")
        finally:
            vad_audio.close()

    def speech_to_intent(self):
        """
        Starts an audio stream and listens to everything mentioned. If any commmands are detected,
        performs inference to determine intent. Returned types of intent are 
        """

        # Initialize libraries
        rhino = None
        pa = None
        stream = None

        try:

            rhino = pvrhino.create(
                library_path=self.rhino_library_path,
                model_path=self.rhino_model_path,
                context_path=self.rhino_context_path
            )

            # Initialize PyAudio and an audio stream
            pa = pyaudio.PyAudio()
            stream = pa.open(
                format = FORMAT,
                channels = CHANNELS,
                rate = rhino.sample_rate,
                input = True, # Specify as input
                frames_per_buffer= rhino.frame_length)

            # Initialize voice activity detector and audio stream with agressiveness between 0 and 3
            spinner = Halo(spinner = 'line', color = 'magenta')
            print(rhino.context_info)

            # Rhino detection
            while True:

                spinner.start()
                pcm = stream.read(rhino.frame_length)
                unpacked = struct.unpack_from("h" * rhino.frame_length, pcm) # Unpack "frame length" amount of "short" data types in C ("h" string) from buffer. Read more on struct Format Strings to understand.
                done = rhino.process(unpacked)

                if done:
                    spinner.stop()
                    result = rhino.get_inference()
                    self.print_intent(result)
                    return 1
        
        except KeyboardInterrupt:
            print("Stopping speech-to-intent detection...")

        finally:
            if rhino is not None:
                rhino.delete()

            if stream is not None:
                stream.close()
            
            if pa is not None:
                pa.terminate()

    def print_intent(self, intent):
        """
        This is the function which can extract speech-to-intent data from Rhino. It is called with an object with "is_understood", "intent" and "slots" getters.
        """
        if intent.is_understood:
            print("Understood intent: {}".format(intent.intent))
            for slot, value in intent.slots.items():
                print("    {} : {}".format(slot, value))
            self.queue.put(1)

        else:
            print("Didn't understand the command.")

    def print_result(self, result):
        """
        This is the function which can extract data from the DeepSpeech engine. It will be called with a string every time something is transcribed by the robot.
        """
        print ("Recognized: {}".format(result))
        return

    def run(self):
    
        """
        Creates an audio stream with PyAudio which constantly listens for the keywords specified.
        If a keyword is detected, self.transcribe() is called to start transcribing commands.
        """
        
        # Extract keywords from keyword_paths
        keywords = list()
        for keyword in self.porc_keyword_paths:
            words = os.path.basename(keyword).replace(".ppn", "").split("_") # Takes the file, deletes .ppn and splits it into a list of strings
            keywords.append(words[0])
        
        # Initialize libraries
        porcupine = None
        pa = None
        stream = None

        try:
            # Initialize wake word detection (Porcupine)
            porcupine = pvporcupine.create(
                library_path = self.porc_library_path,
                model_path = self.porc_model_path,
                keyword_paths = self.porc_keyword_paths,
                sensitivities = self.porc_sensitivities)
            
            # Initialize PyAudio and an audio stream
            pa = pyaudio.PyAudio()
            stream = pa.open(
                format = FORMAT,
                channels = CHANNELS,
                rate = porcupine.sample_rate,
                input = True, # Specify as input
                frames_per_buffer= porcupine.frame_length)
            
            # Print readyness for listening
            print("Listening for keyword with sensitivities:")
            for keyword, sensitivity in zip(keywords, self.porc_sensitivities):
                print("    {} {}".format(keyword, sensitivity))

            # Infinite loop unless self.terminate() called in main thread
            while self.porc_running:

                # Reads porcupine's required frame length of data from audio stream
                pcm = stream.read(porcupine.frame_length)

                # Unpacks the data from a C data type (short) to a Python int
                unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm) # Unpack "frame length" amount of "short" data types in C ("h" string) from buffer. Read more on struct Format Strings to understand.

                # Process data through Porcupine. Returns the index of the keyword from given array if it found one, -1 otherwise
                result = porcupine.process(unpacked)
                if result >= 0:
                    print("Detected keyword {}".format(keywords[result]))

                    # Calls self.transcribe() to start listening for commands. Can be exchanged for any other function to call on keyword detection.
                    # self.transcribe()
                    self.speech_to_intent()
                    print("Done")

        except KeyboardInterrupt:
            print("Stopping wake word detection...")

        finally:
            if porcupine is not None:
                porcupine.delete()

            if stream is not None:
                stream.close()
            
            if pa is not None:
                pa.terminate()
            