import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import tetris_open_game
from display import Display
import pyspiel
import random, time

game = pyspiel.load_game('tetris_game')

display = Display(None)
display.start()

state = game.new_initial_state(show=display)
steps = 0
while not state.is_terminal():
    action = random.choice(state.legal_actions())
    state.apply_action(action)
    steps += 1

print('# of Steps:', steps)
display.close()