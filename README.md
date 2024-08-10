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

You will also need to download portaudio, good luck with that :)

### Windows
You probably will need to compile from source :(

### Mac
Install via Homebrew:
`homebrew install portaudio`

### GNU/Linux (it's not just linux you fools)

I'd just like to interject for a moment. What you’re referring to as Linux, is in fact, GNU/Linux, or as I’ve recently taken to calling it, GNU plus Linux. Linux is not an operating system unto itself, but rather another free component of a fully functioning GNU system made useful by the GNU corelibs, shell utilities and vital system components comprising a full OS as defined by POSIX.
Many computer users run a modified version of the GNU system every day, without realizing it. Through a peculiar turn of events, the version of GNU which is widely used today is often called “Linux”, and many of its users are not aware that it is basically the GNU system, developed by the GNU Project. There really is a Linux, and these people are using it, but it is just a part of the system they use.
Linux is the kernel: the program in the system that allocates the machine’s resources to the other programs that you run. The kernel is an essential part of an operating system, but useless by itself; it can only function in the context of a complete operating system. Linux is normally used in combination with the GNU operating system: the whole system is basically GNU with Linux added, or GNU/Linux. All the so-called “Linux” distributions are really distributions of GNU/Linux.

Right hopefully that scared you off
#### Debian
`sudo apt install portaudio19-dev`
#### Fedora
`sudo dnf install portaudio-devel`
#### Arch Linux
`sudo pacman -S portaudio`

## Configuration
You will need a `config.json` file in your project, with the following fields:
- mode
- div_duration
- scale_filter
- _For mode 1:_
  - req_duration
- _For mode 2:_
  - frequencies

You do not need to include every field, but you need to include the fields required for your mode. Here is an example `config.json`:

```json
{
  "mode": 3,
  "div_duration": 0.5,
  "scale_filter": 5,
  "frequencies": "440,220,880,500",
  "req_duration": 5
}
```

## Usage tips
- Divisions are what the program splits the input into 
  - In recording mode and pure tone mode, the input is split into as many divisions as the user requests.
  - In live mode, the microphone is enabled for the division length.
  - The optimal division length is usually 0.5 seconds
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
