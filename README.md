# Fourier
Fourier is a program that uses the Fast Fourier Transform to take in a sound input with 3 modes: Recording, Pure tone, and Live.

- (1) Recording mode takes in a sound file and outputs the notes in the file.
- (2) Pure tone mode takes in a list of frequencies and applies the fourier transform to find the notes.
- (3) Live mode takes in a sound input from the microphone and outputs the notes every period inputted in every division.

## Installation
You will need the following from PIP:
- numpy
- sounddevice
- scipy
- matplotlib

## Usage tips
- Divisions are what the program splits the input into 
  - In recording mode and pure tone mode, the input is split into as many divisions as the user requests.
  - In live mode, the microphone is enabled for the division length.
  - The optimal division length is usually 0.3 seconds
    - If the division length is too low, the fourier transform won't work properly and the output will be wrong.
    - If the division length is too high, the fourier transform will be applied over a longer audio file, therefore being less accurate. The computation speed for each division will be very slow as well.
- For more accuracy in all modes, you should keep the average modifier between 1 and 1.5 when the texture of the input is thick (lots of notes) and between 1 and 5 when the input is thin (fewer notes). You will need to change this to fit your needs. It should not go below 1.
  - If you receive "No notes found" when the input should have notes, you need to lower the modifier.
  - If you receive lots of notes when the input has no notes, you need to raise the modifier. Be careful, raising this too high could cause actual notes to not be detected.
- Notes are outputted in order of strength, the first in the list is the most dominant and the last is the least dominant. If the modifier is too low, there will be a lot of "noise" in the form of weak notes. Refer to the tip above.


## Gallery
C chord <br />
<img width="204" alt="image" src="https://github.com/iwl-lyam/fourier/assets/64089164/0c9afd9c-b227-4567-b34e-4cb148141e2d">

<br />D chord<br />
<img width="434" alt="image" src="https://github.com/iwl-lyam/fourier/assets/64089164/19e0ec4d-9c35-458e-a723-a0b67c3f525a">

<br />Dm chord<br />
<img width="460" alt="image" src="https://github.com/iwl-lyam/fourier/assets/64089164/1616c589-6447-449a-b9db-7b7185c2830e">
