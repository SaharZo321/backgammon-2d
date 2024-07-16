import pygame
import pygame.gfxdraw
from config import FRAMERATE, BUTTON_COLOR, BUTTON_HOVER_COLOR, OPTIONS_ICON
from graphics.graphics_manager import GraphicsManager, get_font
from backgammon.backgammon import Backgammon
from graphics.button import Button
from graphics.text_button import TextButton
from graphics.outline_text import OutlineText
from menus.options import options_menu
import math


def offline_game(screen: pygame.Surface, clock: pygame.time.Clock):
    run = True
    options = False
    player1_color = pygame.Color(100, 100, 100)
    player2_color = pygame.Color(150, 100, 100)
    graphics = GraphicsManager(
        screen=screen, player1_color=player1_color, player2_color=player2_color
    )
    backgammon = Backgammon()
    last_clicked_index = -1

    def open_options():
        nonlocal options
        options = True

    def close_options():
        nonlocal options
        options = False

    def leave_button_click():
        nonlocal run
        run = False

    def done_button_click():
        if backgammon.is_game_over():
            winner = backgammon.get_winner()
            print(winner)
            backgammon.set_winning_score(winner)
            backgammon.new_game()
            return
        
        backgammon.switch_turn()
        DONE_BUTTON.toggle()

    def undo_button_click():
        backgammon.undo()
        nonlocal highlighted_indexes
        highlighted_indexes = backgammon.get_movable_pieces()

    highlighted_indexes = backgammon.get_movable_pieces()

    buttons_center = math.floor((GraphicsManager.RECT.right + screen.get_width()) / 2)

    DONE_BUTTON = TextButton(
        background_image=None,
        position=(buttons_center, 300),
        text_input="DONE",
        font=get_font(50),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        on_click=done_button_click,
    )

    UNDO_BUTTON = TextButton(
        background_image=None,
        position=(buttons_center, 420),
        text_input="UNDO",
        font=get_font(50),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        on_click=undo_button_click,
    )

    LEAVE_BUTTON = TextButton(
        background_image=None,
        position=(
            math.floor(GraphicsManager.RECT.left / 2),
            math.floor(screen.get_height() / 2),
        ),
        text_input="LEAVE",
        font=get_font(50),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        on_click=leave_button_click,
    )

    SETTINGS_BUTTON = TextButton(
        background_image=OPTIONS_ICON,
        position=(
            screen.get_width() - 45,
            45,
        ),
        text_input="",
        font=get_font(50),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        on_click=open_options,
    )

    DONE_BUTTON.toggle()
    UNDO_BUTTON.toggle()

    game_buttons = [DONE_BUTTON, UNDO_BUTTON, LEAVE_BUTTON, SETTINGS_BUTTON]

    while run:
        clock.tick(FRAMERATE)
        screen.fill("black")
        cursor = pygame.SYSTEM_CURSOR_ARROW
        MOUSE_POSITION = pygame.mouse.get_pos()

        GraphicsManager.render_background(screen=screen)

        graphics.render_board(game_state=backgammon.get_state())

        if last_clicked_index == -1:
            if backgammon.get_captured_pieces() > 0:
                highlighted_indexes = backgammon.get_bar_leaving_positions()
            else:
                highlighted_indexes = backgammon.get_movable_pieces()

        graphics.highlight_tracks(highlighted_indexes)
        if not options and (
            graphics.check_track_input(mouse_position=MOUSE_POSITION) != -1
            or graphics.check_home_track_input(
                mouse_position=MOUSE_POSITION, player=backgammon.current_turn
            )
            or any(button.check_for_input(MOUSE_POSITION) for button in game_buttons)
        ):
            cursor = pygame.SYSTEM_CURSOR_HAND

        DONE_BUTTON.toggle(disabled=not backgammon.is_turn_done())
        UNDO_BUTTON.toggle(disabled=not backgammon.has_history())

        for button in game_buttons:
            button.change_color(MOUSE_POSITION)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN and not options:

                for button in game_buttons:
                    if button.check_for_input(mouse_position=MOUSE_POSITION):
                        button.click()

                if graphics.check_home_track_input(
                    mouse_position=MOUSE_POSITION, player=backgammon.current_turn
                ):
                    backgammon.bear_off(position=last_clicked_index)
                    last_clicked_index = -1

                index = graphics.check_track_input(mouse_position=MOUSE_POSITION)
                if index != -1:

                    if last_clicked_index == -1 and backgammon.get_captured_pieces() == 0:
                        last_clicked_index = index
                        highlighted_indexes = backgammon.get_possible_tracks(
                            last_clicked_index
                        )
                        print(highlighted_indexes)

                    else:
                        if backgammon.get_captured_pieces() > 0:
                            backgammon.leave_bar(end=index)

                        else:
                            backgammon.make_move(start=last_clicked_index, end=index)

                        # a piece had been moved
                        highlighted_indexes = backgammon.get_movable_pieces()
                        last_clicked_index = -1

                    print(last_clicked_index)

        if options:
            options_menu(screen=screen, close=close_options)
        else:
            pygame.mouse.set_cursor(cursor)

        pygame.display.flip()
