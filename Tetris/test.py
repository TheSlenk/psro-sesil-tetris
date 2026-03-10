from tetris import Tetris, Action

env = Tetris(10, 20)

from display import Display
import time

dis = Display()
dis.start()
dis.update(env.get_current_board())
input('continue...')
states = env.get_next_states()
print(states)
for k, v in states.items():
    print(k)
    dis.update(v)
    input('continue...')
dis.stop()