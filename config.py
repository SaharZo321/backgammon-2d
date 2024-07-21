import pygame
from asset import asset
import os

DEFAULT_PLAYER1_COLOR = pygame.Color(100, 100, 100)
DEFAULT_PLAYER2_COLOR = pygame.Color(150, 100, 100)
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
ICON = pygame.transform.scale(
    pygame.image.load(asset(os.path.join("assets", "backgammon.png"))), (60, 60)
)


def get_font(size: int, bold=False, italic=False) -> pygame.font.Font:
    return pygame.font.SysFont("Cooper Black", size, bold, italic)


def get_mid_width() -> int:
    return RESOLUTION[0] / 2
