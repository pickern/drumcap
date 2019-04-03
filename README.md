# Drumcap
Author: Nick Pickering

A little program I wrote when my sampler broke so that I could still easily plunder drum hits 

I typically use it to capture internal audio (so that I do everything in-the-box) on OSX using Soundflower and a Multi-Output Device, but it works for any audio input that PyAudio can detect

### Requirements:
  matplotlib, pyaudio, numpy, wave, tkinter, struct

## Usage:
In the terminal:
  python drumcap.py
  
Then you can select an input, record, playback the recording, highlight selections for different drum kits on the plot, playback individual selections, name your kit, and save

The save function will create an 'output.wav' file of the entire recording in a folder called 'recordings', and will also create a wave file for each selection ('Kick.wav', 'Snare.wav', etc)

If you enter a kit name, the kit name will be added to the beginning of every saved file, so If your kit is 'Kit1.', Save will create 'Kit1.output.wav', 'Kit1.Kick.wav', etc.

## Files:
  drumcap.py:
    Contains main method, gui, and matplotlib functions. Handle all display and control methods.
    
   Recorder.py:
    Manages pyaudio instance and wave methods. Handles all sound and file methods.
