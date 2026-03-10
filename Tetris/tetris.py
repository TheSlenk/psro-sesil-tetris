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
    def __init__(self, id: int, x: int, y: int, color_value: BlockColor):
        self.name = self.__class__.__name__
        self.id = id
        self.x = x
        self.y = y
        self.color_value = color_value
        self.blocks: list[Block] = []

    def rotate(self, amount: int = 90):
        for _ in range((amount % 360) // 90):
            for block in self.blocks:
                x, y = block.x, block.y
                block.x, block.y = -y, x

    def block_positions(self) -> list[tuple[int, int]]:
        positions = []
        for block in self.blocks:
            positions.append((self.x + block.x, self.y + block.y))
        return positions

class LineObstacle(Obstacle):
    def __init__(self, id: int, x: int, y: int):
        super().__init__(id, x, y, BlockColor.BLUE)
        self.blocks.append(Block(-1, 0))
        self.blocks.append(Block(0, 0))
        self.blocks.append(Block(1, 0))
        self.blocks.append(Block(2, 0))

class TObstacle(Obstacle):
    def __init__(self, id: int, x: int, y: int):
        super().__init__(id, x, y, BlockColor.PINK)
        self.blocks.append(Block(-1, 0))
        self.blocks.append(Block(0, 0))
        self.blocks.append(Block(1, 0))
        self.blocks.append(Block(0, -1))

class BoxObstacle(Obstacle):
    def __init__(self, id: int, x: int, y: int):
        super().__init__(id, x, y, BlockColor.YELLOW)
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

    def next_obstacle(self, peice_id: int = None):
        if peice_id is not None or len(self.obstacle_queue) == 0:
            random_obstacle = peice_id if peice_id is not None else random.choice(range(2))
            match random_obstacle:
                case 0:
                    self.current_obstacle = TObstacle(random_obstacle, self.width // 2 - 1, 2)
                case 1:
                    self.current_obstacle = LineObstacle(random_obstacle, self.width // 2 - 1, 2)
                case 2:
                    self.current_obstacle = BoxObstacle(random_obstacle, self.width // 2 - 1, 2)

        else:
            self.current_obstacle = self.obstacle_queue.popleft()

    def get_board_block_value(self, x: int, y: int) -> int:
        return int(self.board[y, x])

    def set_board_block_value(self, x: int, y: int, value):
        self.board[y, x] = value

    def move_obstacle(self, direction: tuple[int, int] = (0, 0), rotation: int = 0) -> bool:
        new_x, new_y = self.current_obstacle.x + direction[0], self.current_obstacle.y + direction[1]
        old_x, old_y = self.current_obstacle.x, self.current_obstacle.y
        rotation_to_old_rotation = 360 - (rotation % 360)
        self.current_obstacle.x, self.current_obstacle.y = new_x, new_y
        self.current_obstacle.rotate(rotation)

        valid = self.validate_obstacle()
        if not valid:
            self.current_obstacle.x, self.current_obstacle.y = old_x, old_y
            self.current_obstacle.rotate(rotation_to_old_rotation)

        return valid

    def validate_obstacle(self) -> bool:
        blocks = self.current_obstacle.block_positions()
        for block in blocks:
            x, y = block
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                return False
            if self.get_board_block_value(x, y) > 0:
                return False

        return True

    def apply_action(self, action: Action):
        x, y = self.current_obstacle.x, self.current_obstacle.y

        match action:
            case Action.LEFT:
                self.move_obstacle(direction=(-1, 0))
            case Action.RIGHT:
                self.move_obstacle(direction=(1, 0))
            case Action.DOWN:
                self.move_obstacle(direction=(0, 1))
            case Action.ROTATE:
                self.move_obstacle(rotation=90)
    
    def get_next_states(self) -> dict:
        states = {}

        peice_name = self.current_obstacle.name
        rotations = (0, 90, 180, 270)
        if peice_name == "LineObstacle" or peice_name == "BoxObstacle":
            rotations = (0, 90)
        
        for rotation in rotations:
            self.move_obstacle(rotation=rotation)
            block_x_pos = [block[0] for block in self.current_obstacle.block_positions()]
            min_x = min(block_x_pos)
            max_x = max(block_x_pos)
            self.reset_obstacle()

            for x in range(-min_x, self.width - max_x):
                self.move_obstacle(direction=(x, 0), rotation=rotation)
                self.drop_obstacle()
                states[(x, rotation)] = self.get_current_board()
                self.reset_obstacle()
        
        return states

    def reset_obstacle(self):
        peice_id = self.current_obstacle.id
        self.next_obstacle(peice_id)

    def drop_obstacle(self):
        while self.move_obstacle(direction=(0, 1)):
            continue

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