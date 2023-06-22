import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import RobotRaconteurCompanion as RRC
from RobotRaconteurCompanion.Util.RobDef import register_service_types_from_resources
from RobotRaconteurCompanion.Util.DateTimeUtil import DateTimeUtil

import sounddevice as sd
import argparse
import sys
from contextlib import suppress
import time
import traceback
import threading
import queue
import numpy as np

# Parser arguments taken from https://python-sounddevice.readthedocs.io/en/0.4.6/examples.html
def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

class MicrophoneImpl:
    def __init__(self, microphone_info):
        # self.microphone_info = microphone_info
        # self.device_info = microphone_info.device_info
        self._stream = None
        self._audio_frame_type = RRN.GetStructureType("experimental.audio.microphone.AudioFrame")
        self._samplerate=0
        self._seqno = 0
        self._wires_init = False
        self._datetime_util = DateTimeUtil(RRN)
        self._record_queues_lock = threading.Lock()
        self._record_queues = []

    def RRServiceObjectInit(self, ctx, service_path):
        
        # self.microphone_stream.MaxBacklog = 2
        
        self.device_clock_now.PeekInValueCallback = lambda ep: self._datetime_util.FillDeviceTime(self._camera_info.device_info,self._seqno)
        self._wires_init = True

    def _open_microphone(self, device, samplerate, channels):
        self._samplerate = int(samplerate)
        self._stream = sd.InputStream(
            device=device, channels=channels,
            samplerate=samplerate, callback=self._audio_callback, latency="low")
        self._stream.start()

    def _close(self):
        s = self._stream
        self._stream = None
        if s is not None:
            s.close()

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
            return
        try:
            self._seqno += 1

            ts = self._datetime_util.TimeSpec3Now()

            a = self._audio_frame_type()
            a.ts = ts
            a.seqno = self._seqno
            a.sample_rate = int(self._samplerate)
            a.audio_data = [np.copy(indata).flatten()]

            if self._wires_init:
                self.microphone_stream.AsyncSendPacket(a, lambda: None)
            
                # device_now = self._datetime_util.FillDeviceTime(self.device_info,self._seqno)
                # self.device_clock_now.OutValue = device_now
            
            with self._record_queues_lock:
                for q in self._record_queues:
                    q.put(a)

        except:
            traceback.print_exc()

    def capture_microphone(self, duration_seconds):
        q = queue.Queue()
        with self._record_queues_lock:
            self._record_queues.append(q)

        ret = []
        try:
            t1 = -1
            t2 = -1
            while t2 - t1 < duration_seconds:
                a = q.get(timeout = 1)
                a_t = a.ts["microseconds"] * 1e-6
                if t1 < 0:
                    t1 = a_t                

                else:
                    t2 = a_t
                ret.append(a)
        finally:
            with self._record_queues_lock:
                self._record_queues.remove(q)
        
        return ret

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-l', '--list-devices', action='store_true', help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(description="Robot Raconteur microphone driver", parents=[parser])
    parser.add_argument('-d', '--device', type=int_or_str, help='input device (numeric ID or substring)')
    parser.add_argument('-r', '--samplerate', type=int, default=44000, help='sampling rate')
    parser.add_argument('-c', '--channels', type=int, default=1, help='number of input channels')
    parser.add_argument("--wait-signal",action='store_const',const=True,default=False, help="wait for SIGTERM orSIGINT (Linux only)")
    args, _ = parser.parse_known_args(remaining)

    RRC.RegisterStdRobDefServiceTypes(RRN)

    register_service_types_from_resources(RRN, __package__, ["experimental.audio.microphone"])

    microphone = MicrophoneImpl(None)
    microphone._open_microphone(args.device, args.samplerate, args.channels)

    try:
        with RR.ServerNodeSetup("experimental.microphone",60828):

            service_ctx = RRN.RegisterService("microphone","experimental.audio.microphone.Microphone",microphone)
            # service_ctx.SetServiceAttributes(microphone_attributes)

            if args.wait_signal:  
                #Wait for shutdown signal if running in service mode          
                print("Press Ctrl-C to quit...")
                import signal
                signal.sigwait([signal.SIGTERM,signal.SIGINT])
            else:            
                input("Server started, press enter to quit...")
            
            microphone._close()
            time.sleep(0.1)
    finally:
        with suppress(Exception):
            microphone._close()






