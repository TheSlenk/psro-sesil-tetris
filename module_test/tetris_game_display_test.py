import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tetris_game import TetrisGame
from display import Display
import random, time

env = TetrisGame(2)
display = Display(env, 400, 400)
display.start()

while not env.is_terminated():
    actions = env.legal_actions()
    action = random.choice(actions)

    env.apply_action(action)
    time.sleep(0.5)

time.sleep(3)
display.close()