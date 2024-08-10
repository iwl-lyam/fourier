"""Fourier, a program to find notes from audio."""

import sys
import numpy as np
import sounddevice as sd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from config import read_config

FS = 44100  # Sampling rate

print('''
  _____                _           
 |  ___|__  _   _ _ __(_) ___ _ __ 
 | |_ / _ \\| | | | '__| |/ _ \\ '__|
 |  _| (_) | |_| | |  | |  __/ |   
 |_|  \\___/ \\__,_|_|  |_|\\___|_|                                      
 ''')


def wave(hz):
    """Takes in a frequency and outputs the sine wave for that frequency"""
    dur = float(input(f"Enter the duration for the {hz} Hz wave in seconds: "))
    return sin(dur, hz)


def sin(dur, hz, am=1):
    """Takes in a frequency and duration (s) and outputs the sin wave"""
    t_s = np.arange(FS * dur)
    return am * np.sin(2 * np.pi * hz * t_s / FS)


def note_sum(waveforms):
    """Takes in waveforms and outputs the note sums"""
    if len(waveforms) == 0:
        return np.zeros_like(waveforms[0])

    waveform_length = len(waveforms[0])
    for wavef in waveforms:
        if len(wavef) != waveform_length:
            raise ValueError("All waveforms must have the same length")

    result_waveform = np.sum(waveforms, axis=0)

    return result_waveform


NUM_SECTIONS = 1000000000000
sections = [None] * 10000

AUDIO = 0
LIVE = False

DURATION = 2
MF = 0.1

CONFIG = read_config()

# mode = input("Select mode (view docs): ")
MODE = str(CONFIG['mode'])
# section_duration = float(
#     input("Enter the duration of each division in seconds: "))  # Duration of each section
SECTION_DURATION = float(CONFIG['div_duration'])

if MODE == "1":
    # DURATION = float(input("Enter the recording duration in seconds: "))
    DURATION = CONFIG['req_duration']
    t_samples = np.arange(FS * DURATION)

    input("Press enter to start recording")

    print("Recording started.")
    AUDIO = sd.rec(int(DURATION * FS), samplerate=FS, channels=1)
    sd.wait()
    print("Recording finished.")

    sd.wait()

    # Flatten audio
    AUDIO = AUDIO.flatten()
    sd.play(AUDIO, FS)
    # Split audio into sections
    NUM_SECTIONS = int(DURATION / SECTION_DURATION)
    sections = np.array_split(AUDIO, NUM_SECTIONS)

elif MODE == "2":

    # values = input("Enter the comma separated values for tone frequencies (Hz): ")
    values = CONFIG['frequencies']
    waveform = note_sum([wave(int(x)) for x in values.split(",")])

    waveform *= MF

    AUDIO = np.int16(waveform * 32767)
    sd.play(AUDIO, FS)
    # Split audio into sections
    NUM_SECTIONS = int(DURATION / SECTION_DURATION)
    sections = np.array_split(AUDIO, NUM_SECTIONS)

elif MODE == "3":
    LIVE = True
else:
    sys.exit("Invalid mode, exiting")


def calculate_frequency(nname):
    """Calculate the notes"""
    # Define the reference frequency of A4 (440 Hz)
    reference_frequency = 440.0

    # Define the mapping between note names and their corresponding steps
    note_steps = {
        'C': -9, 'C#': -8, 'Db': -8,
        'D': -7, 'D#': -6, 'Eb': -6,
        'E': -5,
        'F': -4, 'F#': -3, 'Gb': -3,
        'G': -2, 'G#': -1, 'Ab': -1,
        'A': 0, 'A#': 1, 'Bb': 1,
        'B': 2
    }

    # Extract the note name and octave number from the input
    nname = nname.strip().upper()
    try:
        nt = nname[0]
        octive_ = int(nname[1])
    except ValueError:
        nt = nname[0] + nname[1]
        octive_ = int(nname[2])

    # Calculate the number of steps from A4
    steps = note_steps[nt] + (octive_ - 4) * 12

    # Calculate the frequency using the formula: frequency = reference_frequency * 2^(steps/12)
    frequency_1 = reference_frequency * pow(2, steps / 12)

    return frequency_1


notes = []
# accuracy = float(input('''
# How much do you want the average to be scaled by?
# Put a number between 1 and 1.5 if you have a lot of notes at the same time, and between 1 and
# 3 if you have less notes playing. Change this until you find what fits your audio.'''))
accuracy = CONFIG["scale_filter"]
for i in range(NUM_SECTIONS):
    section = sections[i]
    # print("Analyzing section {}/{}".format(i + 1, num_sections))
    NEW_AUDIO = 0
    if LIVE is True:
        a = sd.rec(int(SECTION_DURATION * FS), samplerate=FS, channels=1)
        sd.wait()
        section = a.flatten()
        section = np.multiply(section, 1000)

    # Apply Fourier Transform
    F = np.fft.fftshift(np.fft.fft(np.fft.fftshift(section))) / len(section)

    # Find frequencies
    freqs = np.fft.fftshift(np.fft.fftfreq(len(section), 1 / FS))

    # Detect peaks
    peaks, _ = find_peaks(np.abs(F))
    peak_frequencies = freqs[peaks]

    positive_peak_frequencies = peak_frequencies[peak_frequencies > 0]

    played_frequencies = []
    note_count = {}

    # print("Positive peak frequencies and musical notes:")
    for freq in positive_peak_frequencies:
        amp = np.abs(F)[np.where(freqs == freq)]
        if freq > 7902.13 or freq < 27 or amp < 0.00004:  # Limit to B8 (7902.13 Hz)
            continue

        played_frequencies.append(freq)

        note = 69 + 12 * np.log2(freq / 440)
        note_name = round(note) % 12
        note_name_dict = {
            0: 'C',
            1: 'C#',
            2: 'D',
            3: 'D#',
            4: 'E',
            5: 'F',
            6: 'F#',
            7: 'G',
            8: 'G#',
            9: 'A',
            10: 'A#',
            11: 'B'
        }
        octave = int((round(note) - 12) / 12)
        note_string = note_name_dict[note_name] + str(octave)
        # print("{:.2f} Hz - {}".format(freq, note_string))

        try:
            if note_count[note_string] < amp.item():
                note_count[note_string] = amp.item()
        except KeyError:
            note_count[note_string] = amp.item()

    note_names_list = list(note_count.keys())
    vals_list = list(note_count.values())

    try:
        AVG = sum(vals_list) / len(note_names_list)

    except ZeroDivisionError:
        AVG = 0

    OUTPUT = ""
    OUTPUT_W = [sin(SECTION_DURATION / 2, 0)]
    WAVE = []

    for note in reversed(sorted(note_count.items(), key=lambda x: x[1])):
        if note[1] > AVG * accuracy:
            frequency = calculate_frequency(note[0])
            OUTPUT_W.append(sin(SECTION_DURATION / 2, frequency))
            OUTPUT += f"{note[0]} "

    # Sum the waveforms correctly
    waveform = note_sum(OUTPUT_W)

    # Normalize the waveform to prevent clipping
    max_val = np.max(np.abs(waveform))
    if max_val > 0:
        waveform = waveform / max_val

    waveform *= MF

    a = np.linspace(0,1,220)

    for j in range(220):
        waveform[j] *= a[j]
        waveform[-j] *= a[j]

    AUDIO = np.int16(waveform * 32767)

    if OUTPUT != "":
        print("Division", str(i) + ":", OUTPUT)
        sd.play(AUDIO, FS)
        sd.wait()
    else:
        print("Division", str(i) + ": No notes found")

    # notes = list(note_count.keys())
    # note_probabilities = list(note_count.values())
    # new_wave = 0

    # print("Building output")
    # for o in range(len(note_count)):
    #     new_wave += wave(calculate_frequency(notes[o])) * note_probabilities[o]

    # input("Press enter to play....")
    # # new_wave *= mf
    # sd.play(new_wave,fs)

    # sd.wait()

    # Create bar chart
    # plt.figure()

    # plt.bar(notes, note_probabilities)
    # plt.xlabel('Note')
    # plt.ylabel('Note Probability')
    # plt.title('Detected Notes - Section {}/{}'.format(i + 1, num_sections))
    # plt.grid(True)
    # plt.show()

plt.plot(freqs, np.abs(F))
plt.plot(freqs[peaks], np.abs(F)[peaks], 'ro')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.title('Real-time Fourier Transform')
plt.grid(True)
plt.show()
