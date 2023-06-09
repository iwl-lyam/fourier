import numpy as np
import sounddevice as sd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

section_duration = float(input("Enter the section duration in seconds: "))  # Duration of each section in seconds
fs = 44100  # Sampling rate

# Record audio
duration = float(input("Enter the recording duration in seconds: "))

# input("Press enter to start recording")

# print("Recording started.")
# audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
# sd.wait()
# print("Recording finished.")

# sd.wait()

# # Flatten audio
# audio = audio.flatten()

def wave(hz):
  global t_samples,fs
  return np.sin(2*np.pi*hz*t_samples/fs)


t_samples = np.arange(fs * duration)
waveform = 0

values = input("Enter comma separated values for tone frequencies (Hz): ")
waveform = sum([ wave(int(x)) for x in values.split(",") ])

waveform *= 0.001
audio = np.int16(waveform * 32767)

sd.play(audio, fs)

# Split audio into sections
num_sections = int(duration / section_duration)
sections = np.array_split(audio, num_sections)



notes = []
for i, section in enumerate(sections):
    print("Analyzing section {}/{}".format(i + 1, num_sections))

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

    print("Positive peak frequencies and musical notes:")
    for freq in positive_peak_frequencies:
        amp = np.abs(F)[np.where(freqs == freq)]
        if freq > 7902.13 or amp < 0.00004:  # Limit to B8 (7902.13 Hz) and amplitude threshold
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
        print("{:.2f} Hz - {}".format(freq, note_string))

        try:

          if note_count[note_string] < amp.item():
            note_count[note_string] = amp.item()
        except:
          note_count[note_string] = amp.item()

    # Create bar chart
    plt.figure()
    notes = list(note_count.keys())
    note_probabilities = list(note_count.values())
    plt.bar(notes, note_probabilities)
    plt.xlabel('Note')
    plt.ylabel('Note Probability')
    plt.title('Detected Notes - Section {}/{}'.format(i + 1, num_sections))
    plt.grid(True)
    plt.show()

plt.plot(freqs, np.abs(F))
plt.plot(freqs[peaks], np.abs(F)[peaks], 'ro') 
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.title('Real-time Fourier Transform')
plt.grid(True)
plt.show()
