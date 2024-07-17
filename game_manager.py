import pygame
import sys
import config
from enum import Enum
from typing import Any

class SettingsKeys(Enum):
    IP = 0
    PIECE_COLOR = 1
    OPPONENT_COLOR = 2


class GameManager:
    clock: pygame.time.Clock
    screen: pygame.Surface
    _settings: dict[SettingsKeys]

    @classmethod
    def start(cls):
        cls._settings = {
            SettingsKeys.IP: "",
            SettingsKeys.OPPONENT_COLOR: pygame.Color(150, 100, 100),
            SettingsKeys.PIECE_COLOR: pygame.Color(100, 100, 100),
        }
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Backgammon")
        cls.clock = pygame.time.Clock()
        cls.screen = pygame.display.set_mode(config.RESOLUTION)
        pygame.display.set_icon(config.ICON)

    @staticmethod
    def quit():
        pygame.quit()
        sys.exit()

    @classmethod
    def set_setting(cls, key: SettingsKeys, value: Any):
        cls._settings[key] = value
        
    @classmethod
    def get_setting(cls, key: SettingsKeys) -> Any:
        return cls._settings[key]
    
    