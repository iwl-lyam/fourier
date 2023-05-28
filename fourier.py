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
omega = 2 * np.pi * np.fft.fftshift(np.fft.fftfreq(N, 1/fs))

print("Detect peaks")
peaks, _ = find_peaks(np.abs(F))

peak_frequencies = omega[peaks]
positive_peak_frequencies = peak_frequencies[peak_frequencies > 0]

print("Creating output audio", len(positive_peak_frequencies))
duration = len(audio) / fs  

chunk_size = 1000  # Number of samples per chunk
composite_tone = np.zeros(len(audio))

# Generate composite tone in smaller chunks
for freq in positive_peak_frequencies:
    tone_chunk = np.sin(2 * np.pi * freq * np.arange(chunk_size) / fs)
    tone_chunk /= np.max(np.abs(tone_chunk))
    for i in range(int(len(audio) / chunk_size)):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size
        composite_tone[start_idx:end_idx] += tone_chunk[:end_idx-start_idx]

composite_tone /= np.max(np.abs(composite_tone))

input("Press enter to play audio")
print("Playing recorded audio...")
sd.play(np.vstack((audio, composite_tone[:len(audio)])).T, samplerate=fs)
sd.wait()

print("Analyzing audio")
print("Plotting audio onto a chart")

plt.plot(omega, np.abs(F))
plt.plot(omega[peaks], np.abs(F)[peaks], 'ro') 
plt.xlabel('Angular Frequency (omega)')
plt.ylabel('Amplitude')
plt.title('Real-time Fourier Transform')
plt.grid(True)
plt.show()
