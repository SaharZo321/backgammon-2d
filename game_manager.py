import pygame
import sys
from config import RESOLUTION

class GameManager():
    clock: pygame.time.Clock
    screen: pygame.Surface
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Backgammon")
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((RESOLUTION[0], RESOLUTION[1]))
        
    @staticmethod    
    def quit():
        pygame.quit()
        sys.exit()




    