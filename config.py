import pygame
from asset import asset
import os


NETWORK_BUFFER = 2048 * 2
GAME_PORT = 6324
RESOLUTION: tuple[int, int] = (1280, 720)
FRAMERATE: int = 60
BUTTON_COLOR = pygame.Color(200, 0, 0)
BUTTON_HOVER_COLOR = pygame.Color(250, 250, 250)
BACKGROUND = pygame.transform.scale(
    pygame.image.load(asset(os.path.join("assets", "background.jpg"))), (1280, 720)
)
OPTIONS_ICON = pygame.transform.scale(
    pygame.image.load(asset(os.path.join("assets", "settings.png"))), (60, 60)
)
