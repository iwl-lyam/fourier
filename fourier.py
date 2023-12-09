import numpy as np
import sounddevice as sd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import sys

fs = 44100  # Sampling rate

print('''
  _____                _           
 |  ___|__  _   _ _ __(_) ___ _ __ 
 | |_ / _ \| | | | '__| |/ _ \ '__|
 |  _| (_) | |_| | |  | |  __/ |   
 |_|  \___/ \__,_|_|  |_|\___|_|                                      
 ''')


def wave(hz):
    global fs
    dur = float(input(f"Enter the duration for the {hz} Hz wave in seconds: "))
    t_s = np.arange(fs * dur)
    return np.sin(2 * np.pi * hz * t_s / fs)


def note_sum(waveforms):
    if len(waveforms) == 0:
        return np.zeros_like(waveforms[0])

    waveform_length = len(waveforms[0])
    for waveform in waveforms:
        if len(waveform) != waveform_length:
            raise ValueError("All waveforms must have the same length")

    result_waveform = np.sum(waveforms, axis=0)

    return result_waveform


num_sections = 1000000000000
sections = [None] * 10000

audio = 0
live = False

duration = 2
mf = 0.1

mode = input("Select mode (view docs): ")
section_duration = float(
    input("Enter the duration of each division in seconds: "))  # Duration of each section in seconds


if mode == "1":
    duration = float(input("Enter the recording duration in seconds: "))
    t_samples = np.arange(fs * duration)

    input("Press enter to start recording")

    print("Recording started.")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    print("Recording finished.")

    sd.wait()

    # Flatten audio
    audio = audio.flatten()
    sd.play(audio, fs)
    # Split audio into sections
    num_sections = int(duration / section_duration)
    sections = np.array_split(audio, num_sections)

elif mode == "2":

    values = input("Enter the comma separated values for tone frequencies (Hz): ")
    waveform = note_sum([wave(int(x)) for x in values.split(",")])

    waveform *= mf

    audio = np.int16(waveform * 32767)
    sd.play(audio, fs)
    # Split audio into sections
    num_sections = int(duration / section_duration)
    sections = np.array_split(audio, num_sections)

elif mode == "3":
    live = True
else:
    sys.exit("Invalid mode, exiting")


def calculate_frequency(note_name):
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
    note_name = note_name.strip().upper()
    try:
        note = note_name[0]
        octave = int(note_name[1])
    except:
        note = note_name[0] + note_name[1]
        octave = int(note_name[2])

    # Calculate the number of steps from A4
    steps = note_steps[note] + (octave - 4) * 12

    # Calculate the frequency using the formula: frequency = reference_frequency * 2^(steps/12)
    frequency = reference_frequency * pow(2, steps / 12)

    return frequency


notes = []
accuracy = float(input('''
How much do you want the average to be scaled by?
Put a number between 1 and 1.5 if you have a lot of notes at the same time, and between 1 and 
3 if you have less notes playing. Mess around with this value until you find what fits your audio.'''))
for i in range(num_sections):
    section = sections[i]
    # print("Analyzing section {}/{}".format(i + 1, num_sections))
    new_audio = 0
    if live is True:
        a = sd.rec(int(section_duration * fs), samplerate=fs, channels=1)
        sd.wait()
        section = a.flatten()
        section = np.multiply(section, 1000)

    # Apply Fourier Transform
    F = np.fft.fftshift(np.fft.fft(np.fft.fftshift(section))) / len(section)

    # Find frequencies
    freqs = np.fft.fftshift(np.fft.fftfreq(len(section), 1 / fs))

    # Detect peaks
    peaks, _ = find_peaks(np.abs(F))
    peak_frequencies = freqs[peaks]

    positive_peak_frequencies = peak_frequencies[peak_frequencies > 0]

    played_frequencies = []
    note_count = {}

    # print("Positive peak frequencies and musical notes:")
    for freq in positive_peak_frequencies:
        amp = np.abs(F)[np.where(freqs == freq)]
        if freq > 7902.13 or freq < 27 or amp < 0.00004:  # Limit to B8 (7902.13 Hz) and amplitude threshold
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
        except:
            note_count[note_string] = amp.item()

    note_names_list = list(note_count.keys())
    vals_list = list(note_count.values())

    try:
        avg = sum(vals_list) / len(note_names_list)

    except ZeroDivisionError:
        avg = 0

    output = ""


    for note in reversed(sorted(note_count.items(), key=lambda x: x[1])):
        if note[1] > avg * accuracy:
            output += f"{note[0]} "

    # print(note_count.keys())
    if output != "":
        print("Division", str(i) + ":", output)
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
