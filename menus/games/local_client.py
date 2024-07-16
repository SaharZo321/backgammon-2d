import pygame
import pygame.gfxdraw
import config
from graphics.graphics_manager import GraphicsManager, get_font, get_mid_width
from backgammon.backgammon import Backgammon
from graphics.button import Button
from graphics.text_button import TextButton
from graphics.outline_text import OutlineText
from menus.options import options_menu
import math
from models.player import Player
from models.move import Move, MoveType
from server.server import BGServer
from game_manager import GameManager
from typing import Callable


def local_client(screen: pygame.Surface, clock: pygame.time.Clock):
    run = True
    player1_color = pygame.Color(100, 100, 100)
    player2_color = pygame.Color(150, 100, 100)
    graphics = GraphicsManager(
        screen=screen, player1_color=player1_color, player2_color=player2_color
    )

    server = BGServer(port=config.GAME_PORT, buffer_size=config.NETWORK_BUFFER)

    current_state = server.get_game_state()

    last_clicked_index = -1

    def quit():
        server.stop()
        GameManager.quit()

    def get_movable_pieces():
        return Backgammon.from_state(current_state).get_movable_pieces()

    def leave_button_click():
        server.stop()
        nonlocal run
        run = False

    def done_button_click():
        nonlocal current_state
        current_state = server.local_done()
        DONE_BUTTON.toggle()
        backgammon = server._get_game()
        if backgammon.is_game_over():
            print(backgammon.get_winner())

    def undo_button_click():
        nonlocal current_state
        current_state = server.local_undo()
        nonlocal highlighted_indexes
        highlighted_indexes = get_movable_pieces()

    def settings_button_click():
        options_menu(screen, clock)

    highlighted_indexes = get_movable_pieces()

    buttons_center = math.floor((GraphicsManager.RECT.right + screen.get_width()) / 2)

    DONE_BUTTON = TextButton(
        background_image=None,
        position=(buttons_center, 300),
        text_input="DONE",
        font=get_font(50),
        base_color=config.BUTTON_COLOR,
        hovering_color=config.BUTTON_HOVER_COLOR,
        on_click=done_button_click,
    )

    UNDO_BUTTON = TextButton(
        background_image=None,
        position=(buttons_center, 420),
        text_input="UNDO",
        font=get_font(50),
        base_color=config.BUTTON_COLOR,
        hovering_color=config.BUTTON_HOVER_COLOR,
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
        base_color=config.BUTTON_COLOR,
        hovering_color=config.BUTTON_HOVER_COLOR,
        on_click=leave_button_click,
    )

    SETTINGS_BUTTON = TextButton(
        background_image=config.SETTINGS_ICON,
        position=(
            screen.get_width() - 45,
            45,
        ),
        text_input="",
        font=get_font(50),
        base_color=config.BUTTON_COLOR,
        hovering_color=config.BUTTON_HOVER_COLOR,
        on_click=settings_button_click,
    )

    DONE_BUTTON.toggle(disabled=current_state.current_turn == Player.player1)
    UNDO_BUTTON.toggle(disabled=True)

    game_buttons = [DONE_BUTTON, UNDO_BUTTON, LEAVE_BUTTON, SETTINGS_BUTTON]

    def is_my_turn() -> bool:
        return current_state.current_turn == Player.player1

    server.start()

    while run:
        clock.tick(config.FRAMERATE)
        screen.fill("black")
        cursor = pygame.SYSTEM_CURSOR_ARROW
        MOUSE_POSITION = pygame.mouse.get_pos()
        GraphicsManager.render_background(screen=screen)

        current_state = server.get_game_state()

        backgammon = Backgammon.from_state(current_state)

        graphics.render_board(current_state)

        if last_clicked_index == -1:
            if backgammon.get_captured_pieces() > 0:
                highlighted_indexes = backgammon.get_bar_leaving_positions()
            else:
                highlighted_indexes = backgammon.get_movable_pieces()

        graphics.highlight_tracks(highlighted_indexes)

        if server.local_is_playing() and (
            (
                is_my_turn()
                and (
                    graphics.check_tracks_input(mouse_position=MOUSE_POSITION)
                    or graphics.check_home_track_input(
                        mouse_position=MOUSE_POSITION, player=backgammon.current_turn
                    )
                )
            )
            or any(button.check_for_input(MOUSE_POSITION) for button in game_buttons)
        ):
            cursor = pygame.SYSTEM_CURSOR_HAND

        DONE_BUTTON.toggle(disabled=not is_my_turn() or not backgammon.is_turn_done())
        UNDO_BUTTON.toggle(disabled=not backgammon.has_history() or not is_my_turn())

        for button in game_buttons:
            button.change_color(MOUSE_POSITION)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and server.local_is_playing()
                and LEAVE_BUTTON.check_for_input(MOUSE_POSITION)
            ):
                LEAVE_BUTTON.click()

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and server.local_is_playing()
                and is_my_turn()
            ):

                for button in game_buttons:
                    if button is LEAVE_BUTTON:
                        continue
                    if button.check_for_input(mouse_position=MOUSE_POSITION):
                        button.click()

                did_hit_target = False
                if graphics.check_home_track_input(
                    mouse_position=MOUSE_POSITION, player=backgammon.current_turn
                ):
                    move = Move(
                        move_type=MoveType.bear_off, start=last_clicked_index, end=24
                    )
                    current_state = server.local_move(move=move)
                    # backgammon.bear_off(position=clicked_index)

                for index in range(24):
                    if graphics.check_track_input(
                        mouse_position=MOUSE_POSITION, index=index
                    ):
                        did_hit_target = True

                        if (
                            last_clicked_index == -1
                            and backgammon.get_captured_pieces() == 0
                        ):
                            last_clicked_index = index
                            highlighted_indexes = backgammon.get_possible_tracks(
                                last_clicked_index
                            )
                            print(highlighted_indexes)

                        else:
                            if backgammon.get_captured_pieces() > 0:
                                move = Move(
                                    move_type=MoveType.leave_bar,
                                    start=backgammon.get_start_position(),
                                    end=index,
                                )
                                current_state = server.local_move(move=move)
                                # backgammon.leave_bar(end=index)

                            else:
                                move = Move(
                                    move_type=MoveType.normal_move,
                                    start=last_clicked_index,
                                    end=index,
                                )
                                current_state = server.local_move(move=move)
                                # backgammon.make_move(start=last_clicked_index, end=index)

                            # a piece had been moved
                            highlighted_indexes = backgammon.get_movable_pieces()
                            last_clicked_index = -1

                last_clicked_index = -1 if not did_hit_target else last_clicked_index
                print(last_clicked_index)

        if server.local_is_alone():
            render_waiting(screen=screen, leave=leave_button_click)

        pygame.mouse.set_cursor(cursor)
        pygame.display.flip()


def render_waiting(screen: pygame.Surface, leave: Callable[[], None]) -> None:
    menu_surface = pygame.Surface(
        size=config.RESOLUTION, flags=pygame.SRCALPHA, depth=32
    )
    menu_surface.convert_alpha()
    menu_surface.fill(pygame.Color(0, 0, 0, 180))
    screen.blit(source=menu_surface, dest=(0, 0))

    PLAYER2_TEXT = OutlineText.render(
        text="PLAYER 2 NOT CONNECTED",
        font=get_font(60),
        gfcolor=pygame.Color("white"),
        ocolor=pygame.Color("black"),
        opx=3,
    )

    PLAYER2_TEXT_RECT = PLAYER2_TEXT.get_rect(center=(get_mid_width(), 200))

    screen.blit(PLAYER2_TEXT, PLAYER2_TEXT_RECT)
    
    WATING_TEXT = OutlineText.render(
        text="WATING",
        font=get_font(80),
        gfcolor=pygame.Color("white"),
        ocolor=pygame.Color("black"),
        opx=3,
    )

    WATING_TEXT_RECT = WATING_TEXT.get_rect(center=(get_mid_width(), 400))

    screen.blit(WATING_TEXT, WATING_TEXT_RECT)

    LEAVE_BUTTON = Button(
        position=(get_mid_width(), 650),
        text_input="LEAVE",
        font=get_font(50),
        base_color=config.BUTTON_COLOR,
        hovering_color=config.BUTTON_HOVER_COLOR,
        on_click=leave,
    )

    MOUSE_POSITION = pygame.mouse.get_pos()

    LEAVE_BUTTON.change_color(MOUSE_POSITION)
    LEAVE_BUTTON.update(screen)

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and LEAVE_BUTTON.check_for_input(
            mouse_position=MOUSE_POSITION
        ):
            LEAVE_BUTTON.click()
