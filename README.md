
# Pinball Lightshow Editor

This project is a Python3 GUI (wxpython) lightshow editor for a custom pinball machine. The tool helps visually create and experiment with pinball LED patterns and timings. The outputs of the tool will be used to describe lightshows to run during game execution.

The project output files are very specific to the custom pinball machine being created, as is the playfield layout and LEDs available.
## Requirements

Included in the project is a requirements.txt file to help install required packages:

pip install -r requirements.txt
## Usage/Examples

The program is started by running:

python3 gui.py
## Demos
LED enabled segments (Pop-bumpers):
![](https://github.com/cdjam/pinball-lightshow-editor/blob/main/demos/01_pops.gif)

LED enabled + random segments:
![](https://github.com/cdjam/pinball-lightshow-editor/blob/main/demos/02_random.gif)

Lightshow segment combos (all segments run at the same time):
![](https://github.com/cdjam/pinball-lightshow-editor/blob/main/demos/03_combo.gif)