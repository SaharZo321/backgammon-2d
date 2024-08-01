from typing import Literal
import pygame
import sys
import config
from models import ColorConverter, Options, Player
from sound_manager import SoundManager


class GameManager:
    clock: pygame.time.Clock
    screen: pygame.Surface
    options = Options(
        ip="",
        player_colors={
            Player.player1: ColorConverter.pygame_to_pydantic(
                pygame.Color(100, 100, 100)
            ),
            Player.player2: ColorConverter.pygame_to_pydantic(
                pygame.Color(150, 100, 100)
            ),
        },
        volume=1,
        mute_volume=1,
    )

    sound_manager: SoundManager

    @classmethod
    def get_sound(cls, key: Literal["button", "timer", "piece", "dice"]):
        return cls.sound_manager.get_sound(key)

    @classmethod
    def set_volume(cls, volume: float):
        cls.options.volume = volume
        cls.sound_manager.set_volume(volume)

    @classmethod
    def start(cls):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        pygame.display.set_caption("Backgammon")
        cls.clock = pygame.time.Clock()
        cls.screen = pygame.display.set_mode(config.RESOLUTION)
        pygame.display.set_icon(config.GAME_ICON)
        cls.sound_manager = SoundManager(
            button=config.BUTTON_SOUND_PATH,
            timer=config.TIMER_SOUND_PATH,
            piece=config.PIECE_SOUND_PATH,
            dice=config.DICE_SOUND_PATH,
        )

    @staticmethod
    def quit():
        pygame.quit()
        sys.exit()

    @classmethod
    def is_window_focused(cls):
        return pygame.key.get_focused()
