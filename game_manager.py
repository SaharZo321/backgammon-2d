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
    )

    sound_manager: SoundManager
    
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
            sounds={
                **config.BUTTON_SOUND.dump(),
                **config.DICE_SOUND.dump(),
                **config.TIMER_SOUND.dump(),
                **config.PIECE_SOUND.dump(),
            }
        )

    @staticmethod
    def quit():
        pygame.quit()
        sys.exit()

    @classmethod
    def is_window_focused(cls):
        return pygame.key.get_focused()
