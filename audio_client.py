from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
import sounddevice as sd
import pyaudio
import wave
import base64
import numpy as np
from array import array
 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5

audio = pyaudio.PyAudio() 


class Client(object):
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
        print ("trying to connect")
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception:
            print ("connection error")
        else:
            print ("connected")
            self.run()

    @gen.coroutine
    def run(self):
        while True:
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
            print ("recording...")
            frames = []
            ff = []     
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)

                #data_chunk=array('h',data)
                
                frames.append(np.fromstring(data, dtype=np.int16))
            numpydata = np.hstack(frames) 
            print(numpydata)
            print(numpydata.shape)
            # sd.play(f, RATE)

            #base_data=base64.b64encode(data)   
            stream.stop_stream()
            stream.close()
                
            print ("finished recording")

            #audio.terminate()
            

            base_data=base64.b64encode(numpydata)
            
            self.ws.write_message(base_data)
           
            

    def keep_alive(self):
        if self.ws is None:
            self.connect()
        else:
            self.ws.write_message("keep alive")

if __name__ == "__main__":
    # make_app().listen(8888)
    client = Client("ws://localhost:3009/audio_stream/recorder-update", 5)
