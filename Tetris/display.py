import pygame
import threading
from enum import Enum

class Color(Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)

class Display:
    def __init__(self, height: int = 800, width: int = 400):
        pygame.init()

        self.screen = pygame.display.set_mode((width, height))
        self.board = None
        self.margin_x = (width * 0.1) // 2
        self.margin_y = (height * 0.1) // 2
        self.cell_size_x = (width * 0.9) // 10
        self.cell_size_y = (height * 0.9) // 20
        self.running = False
    
    def start(self):
        self.running = True

        def play():
            def draw_board():
                rows, cols = self.board.shape
                for row in range(rows):
                    for col in range(cols):
                        trans = (col * self.cell_size_x + self.margin_x, row * self.cell_size_y + self.margin_y, self.cell_size_x, self.cell_size_y)
                        if self.board[row, col] > 0:
                            pygame.draw.rect(self.screen, Color.RED.value, trans)
                        pygame.draw.rect(self.screen, Color.BLACK.value, trans, 1)

            while self.running:
                self.screen.fill(Color.WHITE.value)
                if self.board is not None:
                    draw_board()
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        return

        
        threading.Thread(target = play).start()
    
    def stop(self):
        self.running = False
    
    def update(self, board):
        self.board = board
