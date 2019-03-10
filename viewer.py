import soundfile as sf
import sounddevice as sd
import os
import numpy as np
import wave
from tornado import gen
import time
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.websocket import websocket_connect
import base64
import scipy.io.wavfile as wav

RATE = 44100


class Viewer (object):
    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect()
        PeriodicCallback(self.keep_alive, 20000, io_loop=self.ioloop).start()
        self.ioloop.start()

    @gen.coroutine
    def connect(self):
        print("trying to connect...")
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception:
            print("connection failed...")
            time.sleep(5)
            print("Re-trying connection")
            self.connect()
        else:
            print("connected")
            self.run()
 
    @gen.coroutine
    def run(self):
        while True:
            msg = yield self.ws.read_message()
            if msg is None:
                print("Closing Connection")
                self.ws = None
                break
        
            try:
                print(msg)
                decoded = base64.b64decode(msg)
                buffer2 = np.frombuffer(decoded, dtype=np.int16)
                print("Hi from buffer")
                #data=buffer
                #msg=msg/np.max(np.abs(msg))
                buffer2 = buffer2/np.max(np.abs(buffer2))
                print(buffer2)
                sd.play(buffer2, int(RATE * 1.4))
                wav.write('viewer.wav', int(RATE * 1.4), buffer2)
                #sd.play(data, RATE)
                print("Hi")

            except Exception:
                print('In exception')
            else:
                print('not in exception')

    def keep_alive(self):
        if self.ws is None:
            self.connect()
        else:
            self.ws.write_message("keep alive")         


if __name__ == "__main__":
    voicher = Viewer("ws://localhost:3009/audio_stream/viewer-socket", 5)
