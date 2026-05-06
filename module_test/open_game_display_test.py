import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import tetris_open_game
import pyspiel
import random, time

game = pyspiel.load_game('tetris_game')
state = game.new_initial_state(show=True)

while not state.is_terminal():
    action = random.choice(state.legal_actions())
    state.apply_action(action)

time.sleep(3)