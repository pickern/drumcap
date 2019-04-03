"""
Recorder.py

(v0.2)

Captures and plays back audio from a variety of inputs

Built for drumcap.py

Changes:
    Changed CHUNK from 1024 to 1 for easier coordinate translation
    Made play & save accept start and stop indices
"""
import pyaudio
import wave

class Recorder():
    def __init__(self):
        # pyaudio setup
        self.CHUNK = 1
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 44100
        self.RECORD_SECONDS = 4
        self.WAVE_OUTPUT_FILENAME = "output.wav"
        self.INPUT_INDEX = 0
        self.p = pyaudio.PyAudio()
        self.frames = []

        # organizing inputs for easy reference
        self.INPUT_LIST = []
        self.INPUT_INDEX_DICT = {}
        for i in range(self.p.get_device_count()):
            if self.p.get_device_info_by_index(i).get("maxInputChannels") > 0:
                name = self.p.get_device_info_by_index(i).get("name")
                index = self.p.get_device_info_by_index(i).get("index")
                self.INPUT_LIST.append(name)
                self.INPUT_INDEX_DICT[name] = index

    def record(self, inputdex):
        #open stream
        stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            input_device_index=inputdex
        )

        self.frames = []

        print("* recording")

        # get audio data
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK)
            self.frames.append(data)

        print("* done recording")

        #close stream
        stream.stop_stream()
        stream.close()


    def save(self, start=0, stop=0, name="output.wav", prefix = ""):
        path = 'recordings/'
        #determine start and stop
        trueStart = start
        if start > len(self.frames) or start < 0:
            print("Error: start index out of range")
            return
        if stop > start:
            trueEnd = stop
        else:
            trueEnd = len(self.frames)

        print("Saving {}...".format(name))
        wf = wave.open("{}{}{}".format(path,prefix,name), 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames[trueStart:trueEnd]))
        wf.close()
        print("Save complete")


    def play(self, start=0, stop=0):
        #open stream
        stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            output=True,
            frames_per_buffer=self.CHUNK,
        )
        i = start
        # make sure starting point is within range
        if start > len(self.frames) or start < 0:
            print("Error: start index out of range")
            return
        if stop > start:
            trueEnd = stop
        else:
            trueEnd = len(self.frames)
        # 
        while i < trueEnd:
            stream.write(self.frames[i])
            i += 1

        stream.stop_stream()
        stream.close()


    def quit(self):
        self.p.terminate()
