"""
Drumcap.py v.02

Author: Nick Pickering

Records and displays waveform of 5 seconds of audio from user-specified input

Changes:
    Made editable rectangles for different drum hit

Todo:
    Priority:
    Disconnect
    Add function that adjusts selection start and stop to indices of nearest 0's
        Add a checkbox for "snap selection to zero crossings?"
    Allow changing record_seconds & other settings
        Maybe make a separate setup window before launching the main program

    Bonus:
    Change on_release so that if release happens outside of plot, it will use the nearest edge as the stop
    Make rects editable/dragable/more visual feedback
    Allow adding custom Selections
    Add button for playing the whole kit at once (python might not be fast enough)
        Maybe add a separate play mode
        Add midi support or sequencing for this too
    Add label to kit prefix field
"""
import Recorder
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np
import tkinter as tk
import sys
import struct


# class WaveViewer():
#     def __init__(self):
#         0
class Selection():
    def __init__(self, name, color, rect, start=0,stop=0):
        self.name = name
        self.color = color
        self.rect = rect
        self.start = start
        self.stop = stop

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.rec = Recorder.Recorder()
        self.press = None
        self.rects = self.create_rects()
        self.rectNames = ["Kick", "Snare", "Tom", "HiHat", "Crash", "Ride"]
        self.rectDict = {
            "Kick": 0,
            "Snare": 1,
            "Tom": 2,
            "HiHat": 3,
            "Crash": 4,
            "Ride": 5
        }
        self.activeRectIndex = 0
        self.rectvar = tk.StringVar(self)
        self.rectvar.set(self.rectNames[0])
        self.snapToZX = tk.IntVar(self)
        self.grid()
        self.create_widgets()
        self.connect()

    ##### SETUP METHODS #####
    def create_rects(self):
        names = ["Kick", "Snare", "Tom", "HiHat", "Crash", "Ride"]
        colors = ['r', 'g', 'b', 'y', 'm', 'c']
        rects = []
        for i in range(len(names)):
            rects.append(Selection(names[i], colors[i], None))
        return rects

    def create_widgets(self):
        #### PLOT SETUP ####
        xmin, xmax, ymin, ymax = 0, self.rec.RECORD_SECONDS, -1, 1
        t = np.linspace(0,self.rec.RECORD_SECONDS,self.rec.RECORD_SECONDS*self.rec.RATE)
        self.fig, self.ax = plt.subplots(1,1)
        self.ax.set_xlim(xmin,xmax)
        self.ax.set_ylim(ymin,ymax)
        line, = self.ax.plot(t, t*0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=3)

        #### BUTTONS AND MENUS ####
        inputvar = tk.StringVar(self)
        inputvar.set(self.rec.INPUT_LIST[0])
        #quit button
        self.quit_button = tk.Button(self, text="QUIT", bg="red", command= lambda: self.quit())
        self.quit_button.grid(row=6, column=1)
        #save button
        self.save_button = tk.Button(self, text="Save", fg="red", command= lambda: self.save())
        self.save_button.grid(row=4, column=1, sticky='w')
        #text entry for kit prefix
        tk.Label(self,text="Kit Name:").grid(row=1, sticky='w')
        self.kit_prefix = tk.Entry(self)
        self.kit_prefix.grid(row=1, column=1, sticky='w')
        #rect menu
        tk.Label(self,text="Selection:").grid(row=3, sticky='w')
        self.rect_select = tk.OptionMenu(self, self.rectvar, *self.rectNames)
        self.rect_select.grid(row=3, column=1, sticky='w')
        #play selection button
        self.play_selection_button = tk.Button(self, text="Play Selected", fg="red", command= lambda: self.playSelection())
        self.play_selection_button.grid(row=3, column=1, sticky='e')
        #play button
        self.play_button = tk.Button(self, text="Play", fg="red", command= lambda: self.play())
        self.play_button.grid(row=4, column=1, sticky='e')
        #input menu
        tk.Label(self,text="Input:").grid(row=2, sticky='w')
        self.input_select = tk.OptionMenu(self, inputvar, *self.rec.INPUT_LIST)
        self.input_select.grid(row=2, column=1, sticky='w')
        #record button
        self.rec_button = tk.Button(self, text="Record", fg="red", command= lambda: self.record(self.rec.INPUT_INDEX_DICT[str(inputvar.get())]))
        self.rec_button.grid(row=4, column=1)
    ##### END SETUP METHODS #####

    ##### METHODS #####
    def record(self, inputdex):
        #pipe to rec
        self.rec.record(inputdex)
        self.updatePlot()

    def play(self):
        self.rec.play()

    def playSelection(self):
        #translate data coordinates to indices
        currentSelection = self.rects[self.rectDict[self.rectvar.get()]]
        startIndex = int(currentSelection.start*self.rec.RATE)
        stopIndex = int(currentSelection.stop*self.rec.RATE)
        #if selection isnt made, start = stop = 0, so playSelection() = play()
        self.rec.play(start=startIndex, stop=stopIndex)

    def save(self):
        #full clip
        self.rec.save(prefix=self.kit_prefix.get())
        #save each Selection
        for part in self.rects:
            if part.rect != None:
                #translate indices
                startIndex = int(part.start*self.rec.RATE)
                stopIndex = int(part.stop*self.rec.RATE)
                #save part
                self.rec.save(start=startIndex,stop=stopIndex,name="{}.wav".format(part.name),prefix=self.kit_prefix.get())

    def quit(self):
        #terminate pyaudio
        self.rec.quit()
        #destroy tk instance
        self.master.quit()
        self.master.destroy()

    def updatePlot(self):
        #updates plot with new waveform
        xmin, xmax, ymin, ymax = 0, self.rec.RECORD_SECONDS, -1, 1
        frames = self.rec.frames
        data=[]
        #unpack frames and place in a single array
        for i in range(len(frames)):
            data.append(struct.unpack("{}h".format(2*self.rec.CHUNK),frames[i]))
        #process data
        normData = normalize(np.array(flatten(data)))
        #update plot (could be faster. Maybe use a Line2D directly instead of plot)
        self.ax.clear()
        self.ax.set_xlim(xmin,xmax)
        self.ax.set_ylim(ymin,ymax)
        self.ax.plot(np.linspace(0,self.rec.RECORD_SECONDS,len(normData)), normData)
        self.ax.axhline(color='black')
        self.canvas.draw()

    def zeroCrossing(self, start):
        #incomplete
        #returns index of nearest zero crossing to start index

        #get ydata from the line
        line = self.ax.lines[0]
        data = line.get_ydata()

        #verify start
        if start < 0 or start > len(data):
            print("Error: Start index out of bounds")
            return 0

        #check if we already have a zero
        if data[start] == 0:
            return start

        backSearch = start
        frontSearch = start
        startSign = np.sign(data[start])
        backDone = False
        frontDone = False
        #search on both directions
        while(True):
            if backSearch > 0:
                backSearch -= 1
                if np.sign(data[backSearch]) != startSign:
                    # print(data[backSearch])
                    return backSearch
            else:
                backDone = True
            if frontSearch < len(data):
                frontSearch += 1
                if np.sign(data[frontSearch]) != startSign:
                    # print(data[frontSearch])
                    return frontSearch
            else:
                frontDone = True

            if backDone and frontDone:
                #no zero crossings found, return start
                return start

    ##### END METHODS #####

    ##### EVENT HANDLERS #####
    def connect(self):
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('button_release_event', self.on_release)

    def on_press(self, event):
        #only do stuff within the plot
        if event.inaxes != self.ax:return

        #update press
        self.press = event.xdata, event.ydata
        self.canvas.draw()
        return

    def on_motion(self, event):
        #nothing yet
        if self.press is None: return
        if event.inaxes != self.ax: return

    def on_release(self, event):
        if self.press is None: return

        currentSelection = self.rects[self.rectDict[self.rectvar.get()]]
        #remove rect if it exists
        if currentSelection.rect != None:
            currentSelection.rect.remove()

        # update rect
        currentSelection.start = self.press[0]
        currentSelection.stop = event.xdata
        currentSelection.rect = self.ax.axvspan(currentSelection.start, currentSelection.stop, facecolor=currentSelection.color, alpha=.5)
        self.canvas.draw()

        #clear press
        self.press = None

    def disconnect(self):
        0
    ##### END EVENT HANDLERS #####


#auxilliary methods for array processing
flatten = lambda l : [item for sublist in l for item in sublist]
normalize = lambda l : l/np.max(np.append(l,1.0))

if __name__ == "__main__":
    root=tk.Tk()
    root.title("Capture")
    app = App(master=root)
    app.mainloop()
