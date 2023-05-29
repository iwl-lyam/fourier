import numpy as np
import sounddevice as sd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

duration = float(input("Enter the recording duration in seconds: "))

fs = 44100
N = int(duration * fs)

input("Press enter to start recording")

print("Recording started.")
audio = sd.rec(N, samplerate=fs, channels=1)
sd.wait()
print("Recording finished.")

sd.wait()

print("Flattening audio")
audio = audio.flatten()

print("Apply Fourier Transform")
F = np.fft.fftshift(np.fft.fft(np.fft.fftshift(audio))) / N

print("Find frequencies")
freqs = np.fft.fftshift(np.fft.fftfreq(N, 1/fs))
omega = 2 * np.pi * freqs

print("Detect peaks")
peaks, _ = find_peaks(np.abs(F))

peak_frequencies = omega[peaks]
peak_amplitudes = np.abs(F)[peaks]

positive_peak_frequencies = peak_frequencies[peak_frequencies > 0]
positive_peak_amplitudes = peak_amplitudes[peak_frequencies > 0]

played_frequencies = []
note_count = {}

print("Positive peak frequencies and musical notes:")
for freq, amp in zip(positive_peak_frequencies, positive_peak_amplitudes):
    if freq > 7902.13 or amp < 0.00004:  # Limit to B8 (7902.13 Hz) and minimum amplitude
        continue
    
    played_frequencies.append(freq)
    if freq / 2 in played_frequencies:
        continue
    
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
    
    # Update note count
    if note_string in note_count:
        note_count[note_string] += amp
    else:
        note_count[note_string] = amp

print("Note Count:")
for note, count in note_count.items():
    print("{}: {:.4f}".format(note, count))

# Create bar graph
notes = list(note_count.keys())
counts = list(note_count.values())

plt.bar(notes, counts)
plt.xlabel('Musical Note')
plt.ylabel('Count')
plt.title('Note Count')
plt.grid(True)
plt.show()

print("Creating output audio", len(played_frequencies))
duration = len(audio) / fs

composite_tone = np.zeros_like(audio, dtype=float)

for freq in played_frequencies:
    tone_duration = 0.001  # Tone duration of 1 ms
    num_samples = int(tone_duration * fs)
    tone = np.sin(2 * np.pi * freq * np.arange(num_samples) / fs)
    tone /= np.max(np.abs(tone))
    composite_tone[:num_samples] += tone

composite_tone /= np.max(np.abs(composite_tone))

input("Press enter to play audio")
print("Playing recorded audio and composite tone...")
sd.play(np.column_stack((audio, composite_tone)), samplerate=fs)
sd.wait()

print("Analyzing audio")
print("Plotting audio onto a chart")

plt.plot(freqs, np.abs(F))
plt.plot(freqs[peaks], np.abs(F)[peaks], 'ro') 
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.title('Real-time Fourier Transform')
plt.grid(True)
plt.show()
