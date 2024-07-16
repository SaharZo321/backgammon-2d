import pygame
import sys
import config


class GameManager:
    clock: pygame.time.Clock
    screen: pygame.Surface

    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Backgammon")
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(config.RESOLUTION)
        pygame.display.set_icon(config.ICON)

    @staticmethod
    def quit():
        pygame.quit()
        sys.exit()
