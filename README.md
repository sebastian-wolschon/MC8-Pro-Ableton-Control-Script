# MC8-Pro-Ableton-Control-Script
A barebones script to enable basic transport controls without on-device state management or additional translation of MIDI sent to the device.

## Setup
This script assumes the following configuration:

- Controller receives MIDI on channel 1
- Play Button sends CC55 Value 127 and is located at preset E
- Stop Button sends CC56 Value 127 and is located at preset F
- Record Button sends CC57 Value 127 and is located at preset G

With this, Ableton will send the correct MIDI to toggle the respective buttons into their Active states. The respective preset's Position 1 and Position 2 visuals need to be distict to see it working.
