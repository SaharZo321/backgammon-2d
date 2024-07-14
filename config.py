import pygame

RESOLUTION: tuple[int, int] = (1280, 720)
FRAMERATE: int = 60
BUTTON_COLOR = pygame.Color(200, 0, 0)
BUTTON_HOVER_COLOR = pygame.Color(250, 250, 250)
BACKGROUND = pygame.transform.scale(
    pygame.image.load("assets/background.jpg"), (1280, 720)
)
SETTINGS_ICON = pygame.transform.scale(
    pygame.image.load("assets/settings.png"), (60, 60)
)
