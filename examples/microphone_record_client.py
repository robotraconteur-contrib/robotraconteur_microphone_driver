from RobotRaconteur.Client import *
import sounddevice as sd

# TODO: Read metadata for samplerate and channels
samplerate = 44000
channels = 1


c = RRN.ConnectService('rr+tcp://localhost:60828?service=microphone')

print("Begin recording")
recording = c.capture_microphone(2)
print("End recording")

print("Begin playback")
with sd.OutputStream(channels=channels, samplerate=samplerate) as sd_stream:
    for a in recording:
        for audio_data in a.audio_data:
            sd_stream.write(audio_data)
print("End playback")
