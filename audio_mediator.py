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
#import scipy.io.wavfile as wav



RATE = 44100
class Mediator(object):
    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect()
        PeriodicCallback(self.keep_alive, 250, io_loop=self.ioloop).start()
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
                
                decoded = base64.b64decode(msg)
                buffer = np.frombuffer(decoded, dtype=np.int16)

                data = buffer[:,None]
                print (data.shape)
                samplerate = 44100
                
                newData = np.zeros((data.shape[0] * 2, data.shape[1]))
                
                
                j = 0
                for i in range(data.shape[0]):
                    newData[j] = data[i]
                    newData[j+1] = data[i]
                    j += 2
                #sd.play(newData, samplerate * 1.4)
                newData=newData/np.max(np.abs(newData))
                print("newdata is created")
                
                #base_audio=base64.b64encode(newData)
                #print(base_audio)
                #sd.wait()
                #wav.write('after1.wav', int(samplerate * 1.4), newData)
                sd.play(newData, int(samplerate * 1.4))
                #os.remove()
                
                self.ws.write_message(base_audio)
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
    voicher = Mediator("ws://localhost:3009/audio_stream/mediator-socket", 5)
