from tetris import Tetris, Action

env = Tetris(10, 20)

from display import Display
import time

dis = Display()
dis.start()
dis.update(env.get_current_board())
while True:
    time.sleep(1)
    env.apply_action(Action.DOWN)
    dis.update(env.get_current_board())
dis.stop()