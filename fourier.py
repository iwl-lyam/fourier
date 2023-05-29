import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
from scipy.signal import find_peaks

T = 3
fs = 44100
N = int(T * fs)

input("Press enter to start recording")

print("Recording started.")
audio = sd.rec(int(T * fs), samplerate=fs, channels=1)
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
positive_peak_frequencies = peak_frequencies[peak_frequencies > 0]

print("Creating output audio", len(positive_peak_frequencies))
duration = len(audio) / fs

composite_tone = np.zeros_like(audio, dtype=float)

for freq in positive_peak_frequencies:
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
