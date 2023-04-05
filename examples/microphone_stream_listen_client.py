from RobotRaconteur.Client import *
import sounddevice as sd

# TODO: Read metadata for samplerate and channels
samplerate = 44000
channels = 1


c = RRN.ConnectService('rr+tcp://localhost:60828?service=microphone')

p = c.microphone_stream.Connect(-1)

with sd.OutputStream(channels=channels, samplerate=samplerate) as sd_stream:
    while True:
        audio_frame = p.ReceivePacketWait(timeout=5)
        for audio_data in audio_frame.audio_data:
            sd_stream.write(audio_data)
