import pygame
import sys
import config
from enum import IntEnum, auto
from typing import Any

class SettingsKeys(IntEnum):
    ip = auto()
    piece_color = auto()
    opponent_color = auto()


class GameManager:
    clock: pygame.time.Clock
    screen: pygame.Surface
    _options: dict[SettingsKeys]
    _options_menu: bool

    @classmethod
    def start(cls):
        _options_menu = False
        cls._options = {
            SettingsKeys.ip: "",
            SettingsKeys.opponent_color: pygame.Color(150, 100, 100),
            SettingsKeys.piece_color: pygame.Color(100, 100, 100),
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
        cls._options[key] = value
        
    @classmethod
    def get_setting(cls, key: SettingsKeys) -> Any:
        return cls._options[key]
    
    @classmethod
    def is_window_focused(cls):
        return pygame.key.get_focused()
    