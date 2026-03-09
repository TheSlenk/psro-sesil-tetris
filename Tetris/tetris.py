import random
import numpy as np
from enum import Enum
from collections import deque

class BlockColor(Enum):
    WHITE = 0
    BLACK = 1
    BLUE = 2
    PINK = 3
    YELLOW = 4

class Action(Enum):
    LEFT = 0
    RIGHT = 1
    DOWN = 2
    ROTATE = 3

class Block:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

class Obstacle:
    def __init__(self, x: int, y: int, color_value: BlockColor):
        self.name = self.__class__.__name__
        self.x = x
        self.y = y
        self.color_value = color_value
        self.blocks: list[Block] = []

    def rotate(self, amount: int = 90):
        for i in range((amount % 360) // 90):
            for block in self.blocks:
                x, y = block.x, block.y
                block.x, block.y = -y, x

    def block_positions(self) -> list[tuple[int, int]]:
        positions = []
        for block in self.blocks:
            positions.append((self.x + block.x, self.y + block.y))
        return positions

class LineObstacle(Obstacle):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, BlockColor.BLUE)
        self.blocks.append(Block(-1, 0))
        self.blocks.append(Block(0, 0))
        self.blocks.append(Block(1, 0))
        self.blocks.append(Block(2, 0))

class TObstacle(Obstacle):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, BlockColor.PINK)
        self.blocks.append(Block(-1, 0))
        self.blocks.append(Block(0, 0))
        self.blocks.append(Block(1, 0))
        self.blocks.append(Block(0, -1))

class BoxObstacle(Obstacle):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, BlockColor.YELLOW)
        self.blocks.append(Block(0, 0))
        self.blocks.append(Block(0, -1))
        self.blocks.append(Block(1, 0))
        self.blocks.append(Block(1, -1))


class Tetris:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.board = np.zeros((height, width))

        self.current_obstacle: Obstacle | None = None
        self.obstacle_queue = deque()

        self.next_obstacle()

    def next_obstacle(self):
        if len(self.obstacle_queue) == 0:
            random_obstacle = random.choice(range(2))
            match random_obstacle:
                case 0:
                    self.current_obstacle = TObstacle(self.width // 2 - 1, 2)
                case _:
                    self.current_obstacle = LineObstacle(self.width // 2 - 1, 2)

        else:
            self.current_obstacle = self.obstacle_queue.popleft()

    def get_board_block_value(self, x: int, y: int) -> int:
        return int(self.board[y, x])

    def set_board_block_value(self, x: int, y: int, value):
        self.board[y, x] = value

    def move_obstacle(self, new_x: int, new_y: int, rotation: int = 0) -> bool:
        if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
            return False

        old_x, old_y = self.current_obstacle.x, self.current_obstacle.y
        rotation_to_old_rotation = 360 - (rotation % 360)
        self.current_obstacle.x, self.current_obstacle.y = new_x, new_y
        self.current_obstacle.rotate(rotation)

        collided = self.check_obstacle_collision()
        if collided:
            self.current_obstacle.x, self.current_obstacle.y = old_x, old_y
            self.current_obstacle.rotate(rotation_to_old_rotation)

        return collided

    def check_obstacle_collision(self) -> bool:
        blocks = self.current_obstacle.block_positions()
        for block in blocks:
            if self.get_board_block_value(block[0], block[1]) > 0:
                return True

        return False

    def apply_action(self, action: Action):
        x, y = self.current_obstacle.x, self.current_obstacle.y

        match action:
            case Action.LEFT:
                self.move_obstacle(x - 1, y)
            case Action.RIGHT:
                self.move_obstacle(x + 1, y)
            case Action.DOWN:
                self.move_obstacle(x, y + 1)
            case Action.ROTATE:
                self.move_obstacle(x, y, 90)

    def play(self, action: Action):
        self.apply_action(action)

    def print_board(self):
        print(self)

    def get_current_board(self):
        current_obstacle_position = self.current_obstacle.block_positions()
        copy_board = self.board.copy()
        for (x, y) in current_obstacle_position:
            copy_board[y, x] = self.current_obstacle.color_value.value
        
        return copy_board

    def __str__(self):
        return str(self.get_current_board())