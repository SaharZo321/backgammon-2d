from enum import Enum
import math
from backgammon import Backgammon
import config
from graphics.buttons import Button


import pygame


from typing import Callable

from graphics.graphics_manager import GraphicsManager, get_font


class Screen:
    @classmethod
    def start(cls, screen: pygame.Surface, clock: pygame.time.Clock):
        pass

    @classmethod
    def _check_buttons(
        cls, screen: pygame.Surface, buttons: list[Button], condition=True
    ):
        """Updates all buttons on a given screen. Returns a matching hand or arrow cursor.

        Args:
            screen (pygame.Surface): The screen the buttons are rendered on.
            buttons (list[Button]): List of buttons to update.

        Returns:
            pygame cursor (int)
        """
        mouse_position = pygame.mouse.get_pos()

        for button in buttons:
            if condition:
                button.change_color(mouse_position)
            button.update(screen)

        if (
            any(button.check_for_input(mouse_position) for button in buttons)
            and condition
        ):
            return pygame.SYSTEM_CURSOR_HAND
        else:
            return pygame.SYSTEM_CURSOR_ARROW

    @classmethod
    def _click_buttons(cls, buttons: list[Button]):
        mouse_position = pygame.mouse.get_pos()

        for button in buttons:
            if button.check_for_input(mouse_position):
                button.click()

    @classmethod
    def _next_text(
        cls,
        event: pygame.event.Event,
        current_text: str = "",
        on_escape: Callable[[], None] = lambda: None,
        on_enter: Callable[[], None] = lambda: None,
    ) -> str:
        if event.key == pygame.K_BACKSPACE:
            # get text input from 0 to -1 i.e. end.
            return current_text[:-1]
        elif event.key == pygame.K_ESCAPE:
            on_escape()
        elif event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
            on_enter()
        else:
            # Unicode standard is used for string formation
            return current_text + event.unicode
        return current_text

    @classmethod
    def _check_quit(cls, event: pygame.event.Event, quit: Callable[[], None]):
        if event.type == pygame.QUIT:
            quit()


class GameScreenButtonKeys(Enum):
    DONE = "done",
    UNDO = "undo",
    LEAVE = "leave",
    OPTIONS = "options",

class GameScreen(Screen):

    @classmethod
    def _get_highlighted_tracks(cls, graphics: GraphicsManager, backgammon: Backgammon):
        mouse_position = pygame.mouse.get_pos()
        index = graphics.check_track_input(mouse_position=mouse_position)
        if backgammon.get_captured_pieces() > 0:
            return backgammon.get_bar_leaving_positions()
        elif index != -1 and backgammon.is_start_valid(index):
            possible_tracks = backgammon.get_possible_tracks(index)
            return possible_tracks + [index] if len(possible_tracks) > 0 else []
        else:
            return backgammon.get_movable_pieces()

    @classmethod
    def get_cursor(
        cls,
        graphics: GraphicsManager,
        buttons: list[Button],
        backgammon: Backgammon,
        condition=True,
    ):
        mouse_position = pygame.mouse.get_pos()

        if condition and (
            graphics.check_track_input(mouse_position=mouse_position) != -1
            or graphics.check_home_track_input(
                mouse_position=mouse_position, player=backgammon.current_turn
            )
            or any(button.check_for_input(mouse_position) for button in buttons)
        ):
            return pygame.SYSTEM_CURSOR_HAND
        return pygame.SYSTEM_CURSOR_ARROW

    @classmethod
    def _check_buttons(
        cls, screen: pygame.Surface, buttons: list[Button], condition=True
    ):
        mouse_position = pygame.mouse.get_pos()

        for button in buttons:
            if condition:
                button.change_color(mouse_position)
            button.update(screen)

    @classmethod
    def _move_piece(
        cls,
        on_bear_off: Callable[[int], None],
        on_normal_move: Callable[[int], None],
        on_leave_bar: Callable[[int], None],
        on_choose_piece: Callable[[int], None],
        on_random_click: Callable[[], None],
        graphics: GraphicsManager,
        backgammon: Backgammon,
        last_clicked_index: int,
    ):
        mouse_position = pygame.mouse.get_pos()
        if graphics.check_home_track_input(
            mouse_position=mouse_position, player=backgammon.current_turn
        ):
            on_bear_off(last_clicked_index)

        index = graphics.check_track_input(mouse_position=mouse_position)
        if index != -1:  # clicked on track
            if (
                last_clicked_index == -1
                and backgammon.get_captured_pieces() == 0
            ):  # clicked on a movable piece
                on_choose_piece(index)

            else:
                if backgammon.get_captured_pieces() > 0:
                    on_leave_bar(index)
                else:
                    on_normal_move(index)

            print(last_clicked_index)
        else:  # clicked not on a track
            on_random_click()

    @classmethod
    def _get_buttons(
        cls,
        on_leave: Callable[[], None],
        on_options: Callable[[], None],
        on_done: Callable[[int], None],
        on_undo: Callable[[int], None],
        graphics: GraphicsManager,
    ):
        right_center = math.floor((graphics.RECT.right + config.RESOLUTION[0]) / 2)
        left_center = math.floor(graphics.RECT.left / 2)
        
        DONE_BUTTON = Button(
            background_image=None,
            position=(right_center, 300),
            text_input="DONE",
            font=get_font(50),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            on_click=on_done,
        )

        UNDO_BUTTON = Button(
            background_image=None,
            position=(right_center, 420),
            text_input="UNDO",
            font=get_font(50),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            on_click=on_undo,
        )

        LEAVE_BUTTON = Button(
            background_image=None,
            position=(
                left_center,
                math.floor(config.RESOLUTION[1] / 2),
            ),
            text_input="LEAVE",
            font=get_font(50),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            on_click=on_leave,
        )

        OPTIONS_BUTTON = Button(
            background_image=config.OPTIONS_ICON,
            position=(
                config.RESOLUTION[0] - 45,
                45,
            ),
            text_input="",
            font=get_font(50),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            on_click=on_options,
        )

        DONE_BUTTON.toggle()
        UNDO_BUTTON.toggle()
        
        return {
            GameScreenButtonKeys.DONE: DONE_BUTTON,
            GameScreenButtonKeys.UNDO: UNDO_BUTTON,
            GameScreenButtonKeys.LEAVE: LEAVE_BUTTON,
            GameScreenButtonKeys.OPTIONS: OPTIONS_BUTTON
        }
    
