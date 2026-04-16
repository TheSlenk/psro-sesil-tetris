import pygame
import threading
from enum import Enum
from tetris import BlockColor

class Color(Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    PINK = (255, 192, 203)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    GREEN = (0, 255, 0)
    ORANGE = (255, 165, 0)
    GREY = (190, 190, 190)

tetris_colors = {
    BlockColor.BLUE.value: Color.BLUE.value,
    BlockColor.PINK.value: Color.PINK.value,
    BlockColor.YELLOW.value: Color.YELLOW.value,
    BlockColor.CYAN.value: Color.CYAN.value,
    BlockColor.GREEN.value: Color.GREEN.value,
    BlockColor.ORANGE.value: Color.ORANGE.value,
    BlockColor.RED.value: Color.RED.value
}

class Display:
    def __init__(self, num_players: int = 2, height: int = 800, width: int = 800):
        pygame.init()

        self.screen = pygame.display.set_mode((width, height))
        self.player_width = width // num_players
        self.player_height = height
        self.boards: list[tuple] = []
        self.margin_x = (self.player_width * 0.1) // 2
        self.margin_y = (self.player_height * 0.1) // 2
        self.cell_size_x = (self.player_width * 0.9) // 10
        self.cell_size_y = (self.player_height * 0.9) // 20
        self.running = False
    
    def start(self):
        self.running = True

        def play():
            def draw_board(index: int, board, done: bool):
                rows, cols = board.shape
                for row in range(rows):
                    for col in range(cols):
                        trans = (col * self.cell_size_x + self.margin_x + (index * self.player_width), row * self.cell_size_y + self.margin_y, self.cell_size_x, self.cell_size_y)
                        value = board[row, col]

                        if value > 0:
                            pygame.draw.rect(self.screen, tetris_colors[value], trans)
                        elif done:
                            pygame.draw.rect(self.screen, Color.GREY.value, trans)
                        pygame.draw.rect(self.screen, Color.BLACK.value, trans, 1)

            while self.running:
                self.screen.fill(Color.WHITE.value)
                if len(self.boards) > 0:
                    for index, (board, done) in enumerate(self.boards):
                        draw_board(index, board, done)
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        return

        
        threading.Thread(target = play).start()
    
    def change_caption(self, message: str):
        pygame.display.set_caption(message)
    
    def stop(self):
        self.running = False
    
    def update(self, boards: list[tuple]):
        self.boards = boards
