# EC535 Final Project: Electronic Instrument Simulator
## Author: Team 13: Hin Lui Shum


This final project is a electronic musical instrument using a BeagleBone Black that includes interactive menu controls to switch between different functionalities like recording, playback, and switching between instrument choices of piano and guitar.

## Features

- **Multiple Instrument Sounds**: Switch between different instruments like piano and guitar.
- **Recording Capability**: Record the sequences of notes played.
- **Playback Functionality**: Play back recorded sequences.
- **Menu System**: Interact with the instrument through a menu system using specific notes to navigate and select options.

## Hardware Requirements
- BeagleBone Black revc
- 16GB micro SD card
- Breadboard and connecting wires
- Push buttons for controls
- 10k Ohms Resistors
- USB port speaker
- USB Hub (Optional)
- USB Wifi Adapter (Optional)

## Software Requirements / Used
- Am335x Debian 11.7
- Python 3.x
- Pygame library for handling audio outputs
- Adafruit_BBIO.GPIO  library for GPIO pin control
- Balena Etcher for flashing drives

## Setup and Installation
With Debian 11.7 installed the login:password would be [debian:temppwd]. Python 3.X comes preinstalled. Follow the circuit below to set up the pins and circuit.

1. **Setup Circuit & Hardwares**:

2. **Setup Python Environment**:
   pip3 install pygame RPi.GPIO

3. **Clone the Repository**:
   git clone [https://github.com/yourgithub/yourproject.git](https://github.com/jshumhl/EC535_Project.git)
   
4. **Running the Script:**:
   python __main__.py
