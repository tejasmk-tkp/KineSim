#!/bin/bash

# Open the first terminal tab and run the first script
alacritty --command bash -c 'source .venv/bin/activate && python3 simulation.py' &
# Open the second terminal tab and run the second script

alacritty --command bash -c 'source ../control_interface/.venv/bin/activate && python3 ../control_interface/controller.py'
