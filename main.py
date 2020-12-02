# Main robot control file
import speech
import deepspeech                           # Machine learning model library
import numpy as np                          # Numpy for audio buffer data arrays
#import motors
from subprocess import call                 # Send commands to Pi. Mostly used to program shutdown button.
from time import sleep                      # Delay function
#import sensor
#import pigpio                               # Raspberry Pi Pin control
import os                                   # Get path function
from halo import Halo                       # Animated spinners for loading
from time import perf_counter as timer   # Timer to time model load speed

# TODO: Transfer to normal pbmm deepspeech model compatible with Pi
# TODO: Implement Spinner to recognizing audio


# Pin Definitions

# Initialize motors
# motor1 = motors.Motor(0,0) # Left
# motor2 = motors.Motor(0,0) # Right
# motorGroup = [motor1, motor2]

# Initialize motor controller
# motorControl = motors.MotorController(motorGroup)

def main():
    # while True:
    # TODO: Reset pins at shutdown
    # init_speech_model("deepspeech-0.8.2-models.tflite", aggressiveness=1)
    recognizer = speech.Recognizer("deepspeech-0.8.2-models.tflite")
    recognizer.run()
    print("Program closing")

def init_speech_model(modelname, scorername = None, use_scorer = False, aggressiveness = 0):
    """
    Initialize Audio Stream, Voice Activity Detection and Deepspeech Decoding Algorithm
    """
    # Initialize DeepSpeech model
    modelPath = str(os.path.join(os.getcwd(), "model", modelname))
    print("Trying to open model at {}".format(modelPath))
    modelLoadStart = timer()
    ds = deepspeech.Model(modelPath)
    modelLoadEnd = timer()
    print("Successfully loaded model in {:.3}s".format(modelLoadEnd - modelLoadStart))

    # Initialize scorer
    if use_scorer:
        scorerPath = str(os.path.join(os.getcwd(), "model", scorername))
        if os.path.exists(scorerPath):
            scorerLoadStart = timer()
            ds.enableExternalScorer(modelPath)
            scorerLoadEnd = timer()
            print("Successfully loaded scorer in {:.3}s".format(scorerLoadEnd - scorerLoadStart))
            
    # Initialize voice activity detector and audio stream with agressiveness between 0 and 3
    vad_audio = speech.VoiceActivityDetector(aggressiveness)
    print("Listening to input (ctrl-C to exit)")
    frames = vad_audio.vad_collector()

    # Init loading bar
    spinner = Halo(spinner = 'line', color = 'magenta')

    # Start stream and transcribing
    try:
        modelStream = ds.createStream()

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
                modelStream = ds.createStream()
    except KeyboardInterrupt:
        print("Stopping recording...")
    finally:
        vad_audio.close()


#def shutdown():
#    """Shut down system by passing a commmand to commmand line."""
#
#    call(["sudo", "shutdown", "-h", "now"]) # "Sudo" for admin rights, "-h" for halting after shutting down processes

if __name__ == "__main__":
    main()
