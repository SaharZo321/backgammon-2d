from enum import StrEnum, auto
import math
import time
from backgammon import Backgammon, BackgammonAI
import config
from config import get_font
from decorators import debounce
from game_manager import GameManager
from graphics.elements import ButtonElement, Element, TimerElement
import pygame
from typing import Callable
from graphics.graphics_manager import GraphicsManager
from graphics.styled_elements import StyledButton
from models import ColorConverter, Move, Player, Position, ScoredMoves


class Screen:
    @classmethod
    def start(cls, screen: pygame.Surface, clock: pygame.time.Clock):
        pass
        raise NotImplementedError()

    @classmethod
    def render_elements(
        cls,
        screen: pygame.Surface,
        elements: list[Element],
        events: list[pygame.event.Event],
        update_condition=True,
    ):
        for element in elements:
            if update_condition:
                element.update(events)
            element.render(screen)

    @classmethod
    def _get_cursor(cls, elements: list[Element], condition=True):
        if any(button.is_input_recieved() for button in elements) and condition:
            return pygame.SYSTEM_CURSOR_HAND
        return pygame.SYSTEM_CURSOR_ARROW

    @classmethod
    def click_elements(cls, elements: list[Element], events: list[pygame.event.Event]):
        clicked = False
        for element in elements:
            clicked = element.click(events)
            if clicked:
                break

    @classmethod
    def check_quit(cls, events: list[pygame.event.Event], quit: Callable[[], None]):
        if any(event.type == pygame.QUIT for event in events):
            quit()


class GameScreenElementKeys(StrEnum):
    done = auto()
    undo = auto()
    leave = auto()
    options = auto()
    timer = auto()


class GameScreen(Screen):

    done_button = StyledButton(
        text_input="DONE",
        font=get_font(50),
    )

    undo_button = StyledButton(
        text_input="UNDO",
        font=get_font(50),
    )

    leave_button = StyledButton(
        text_input="LEAVE",
        font=get_font(50),
    )

    options_button = StyledButton(
        image=config.OPTIONS_ICON,
    )

    timer = TimerElement(
        font=get_font(50),
        timer_type="sec",
        threshold=10,
        threshold_sound=GameManager.sound_manager.get_sound(config.TIMER_SOUND.key),
    )

    game_buttons = [done_button, undo_button]
    always_on_buttons = [leave_button, options_button]
    all_elements: list[Element] = game_buttons + always_on_buttons + [timer]

    ai_moves: list[Move]
    bot = False
    bot_current_time: float = 0
    backgammon: Backgammon
    run = True
    options = False
    graphics: GraphicsManager
    last_clicked_index = -1
    highlighted_indexes: list[int] = []

    @classmethod
    @debounce(0.1)
    def play_piece_sound(cls):
        GameManager.sound_manager.play(config.PIECE_SOUND.key)

    @classmethod
    def get_highlighted_tracks(cls):
        index = cls.last_clicked_index
        if cls.backgammon.get_captured_pieces() > 0:
            return cls.backgammon.get_bar_leaving_positions()
        elif index != -1 and cls.backgammon.is_start_valid(index):
            possible_tracks = cls.backgammon.get_possible_tracks(index)
            return possible_tracks + [index] if len(possible_tracks) > 0 else []
        else:
            return cls.backgammon.get_movable_pieces()

    @classmethod
    def get_cursor(
        cls,
        elements: list[ButtonElement],
        condition=True,
    ):

        if condition and (
            cls.graphics.check_track_input() != -1
            or cls.graphics.check_home_track_input(player=cls.backgammon.current_turn)
            or any(button.is_input_recieved() for button in elements)
        ):
            return pygame.SYSTEM_CURSOR_HAND
        return pygame.SYSTEM_CURSOR_ARROW

    @classmethod
    def move_piece(cls, events: list[pygame.event.Event]):
        if not any(
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            for event in events
        ):
            return

        index = cls.graphics.check_track_input()

        if cls.graphics.check_home_track_input(player=cls.backgammon.current_turn):
            cls.on_bear_off()
            cls.play_piece_sound()
        elif index != -1:  # clicked on track
            if (
                cls.last_clicked_index == -1
                and cls.backgammon.get_captured_pieces() == 0
            ):  # clicked on a movable piece
                cls.on_choose_piece(index)

            else:
                if cls.backgammon.get_captured_pieces() > 0:
                    cls.on_leave_bar(index)
                    cls.play_piece_sound()

                else:
                    cls.on_normal_move(index)
                    cls.play_piece_sound()

            print(cls.last_clicked_index)
        else:  # clicked not on a track
            cls.on_random_click()

    @classmethod
    def set_up_elements(cls):
        right_center = math.floor((cls.graphics.RECT.right + config.RESOLUTION[0]) / 2)
        left_center = math.floor(cls.graphics.RECT.left / 2)

        cls.done_button.disabled = True
        cls.done_button.position = Position(
            anchor="midbottom", coords=(right_center, config.SCREEN.centery)
        )
        cls.done_button.on_click = cls.done_turn

        cls.leave_button.position = Position(
            coords=(left_center, config.SCREEN.centery)
        )
        cls.leave_button.on_click = cls.stop

        cls.options_button.position = Position(
            anchor="topright", coords=(config.SCREEN.width - 12, 12)
        )
        cls.options_button.on_click = cls.open_options

        cls.undo_button.position = Position(
            anchor="midtop", coords=(right_center, config.SCREEN.centery)
        )
        cls.undo_button.on_click = cls.undo_move

        cls.timer.position = Position(coords=(right_center, 200))
        cls.timer.on_done = cls.setup_bot

    @classmethod
    def start_timer(cls):
        cls.timer.start(config.TIMER)
        GameManager.sound_manager.play(config.DICE_SOUND.key)

    @classmethod
    def setup_bot(cls):
        cls.bot = True
        if cls.backgammon.is_turn_done():
            cls.ai_moves = []
            return
        
        def save_ai_moves(scored_moves: ScoredMoves):
            cls.ai_moves = scored_moves.moves
            print(cls.ai_moves)
            
        cls.bot_current_time = time.time()
        BackgammonAI.get_best_move(game=cls.backgammon, callback=save_ai_moves)

    @classmethod
    def move_bot(
        cls,
        on_game_over: Callable[[], None] = lambda: None,
        on_move: Callable[[Move], None] = lambda x: None,
    ):
        cls.bot_current_time = time.time()
        if len(cls.ai_moves) == 0:
            print("bot played")
            cls.bot = False
            if cls.backgammon.is_game_over():
                on_game_over()
                return
            cls.done_turn()
        else:
            cls.play_piece_sound()
            move = cls.ai_moves.pop()
            print("Handled Move: ", move)
            cls.backgammon.handle_move(move=move)
            on_move(move)

    @classmethod
    def is_my_turn(cls):
        pass
        raise NotImplementedError

    @classmethod
    def is_screen_on_top(cls):
        pass
        raise NotImplementedError

    @classmethod
    def open_options(cls):
        cls.options = True

    @classmethod
    def close_options(cls):
        cls.options = False

    @classmethod
    def stop(cls):
        pass
        raise NotImplementedError

    @classmethod
    def on_random_click(cls):
        pass
        raise NotImplementedError

    @classmethod
    def on_normal_move(cls, clicked_index: int):
        pass
        raise NotImplementedError

    @classmethod
    def on_leave_bar(cls, clicked_index: int):
        pass
        raise NotImplementedError

    @classmethod
    def on_bear_off(cls):
        pass
        raise NotImplementedError

    @classmethod
    def on_choose_piece(cls, clicked_index: int):
        pass
        raise NotImplementedError

    @classmethod
    def highlight_tracks(cls, is_my_turn=True):
        cls.highlighted_indexes = []

        if not cls.is_screen_on_top() and not cls.bot and is_my_turn:
            cls.highlighted_indexes = cls.get_highlighted_tracks()

        cls.graphics.highlight_tracks(cls.highlighted_indexes)

    @classmethod
    def done_turn(cls):
        pass
        raise NotImplementedError

    @classmethod
    def undo_move(cls):
        pass
        raise NotImplementedError

    @classmethod
    def render_board(cls, is_online=True, opponent_color: pygame.Color | None = None):
        player_colors = {
            Player.player1: ColorConverter.pydantic_to_pygame(
                GameManager.options.player_colors[Player.player1]
            ),
            Player.player2: (
                ColorConverter.pydantic_to_pygame(
                    GameManager.options.player_colors[Player.player2]
                )
                if opponent_color is None
                else opponent_color
            ),
        }
        cls.graphics.render_board(
            game_state=cls.backgammon.state,
            player_colors=player_colors,
            is_online=is_online,
        )

    @classmethod
    def update_game_buttons(cls):
        cls.done_button.disabled = (
            not cls.backgammon.is_turn_done() or not cls.is_my_turn() or cls.bot
        )
        cls.undo_button.disabled = (
            not cls.has_history() or not cls.is_my_turn() or cls.bot
        )

    @classmethod
    def has_history(cls):
        pass
        raise NotImplementedError
