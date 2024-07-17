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
from game_manager import GameManager, SettingsKeys
from typing import Callable
from models.game_state import OnlineGameState, ColorConverter


def local_client(screen: pygame.Surface, clock: pygame.time.Clock):
    run = True
    options = False
    graphics = GraphicsManager(screen=screen)

    server = BGServer(
        port=config.GAME_PORT,
        buffer_size=config.NETWORK_BUFFER,
        local_color=ColorConverter.pygame_to_pydantic(GameManager.get_setting(SettingsKeys.PIECE_COLOR)),
        online_color=ColorConverter.pygame_to_pydantic(GameManager.get_setting(SettingsKeys.OPPONENT_COLOR)),
    )

    current_state = server.local_get_game_state()

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

    def save_state(state: OnlineGameState):
        nonlocal current_state
        current_state = state

    def done_button_click():
        save_state(server.local_done())
        DONE_BUTTON.toggle()
        backgammon = Backgammon.from_state(current_state)
        if backgammon.is_game_over():
            print(backgammon.get_winner())

    def undo_button_click():
        save_state(server.local_undo())
        nonlocal highlighted_indexes
        highlighted_indexes = get_movable_pieces()

    def open_options():
        nonlocal options
        options = True

    def close_options():
        nonlocal options
        options = False

    highlighted_indexes = get_movable_pieces()

    right_center = math.floor((graphics.RECT.right + screen.get_width()) / 2)
    left_center = math.floor((graphics.RECT.left) / 2)

    DONE_BUTTON = TextButton(
        background_image=None,
        position=(right_center, 300),
        text_input="DONE",
        font=get_font(50),
        base_color=config.BUTTON_COLOR,
        hovering_color=config.BUTTON_HOVER_COLOR,
        on_click=done_button_click,
    )

    UNDO_BUTTON = TextButton(
        background_image=None,
        position=(right_center, 420),
        text_input="UNDO",
        font=get_font(50),
        base_color=config.BUTTON_COLOR,
        hovering_color=config.BUTTON_HOVER_COLOR,
        on_click=undo_button_click,
    )

    LEAVE_BUTTON = TextButton(
        background_image=None,
        position=(
            left_center,
            math.floor(screen.get_height() / 2),
        ),
        text_input="LEAVE",
        font=get_font(50),
        base_color=config.BUTTON_COLOR,
        hovering_color=config.BUTTON_HOVER_COLOR,
        on_click=leave_button_click,
    )

    SETTINGS_BUTTON = TextButton(
        background_image=config.OPTIONS_ICON,
        position=(
            screen.get_width() - 45,
            45,
        ),
        text_input="",
        font=get_font(50),
        on_click=open_options,
    )

    DONE_BUTTON.toggle(disabled=current_state.current_turn == Player.player1)
    UNDO_BUTTON.toggle(disabled=True)

    game_buttons = [DONE_BUTTON, UNDO_BUTTON]
    always_on_buttons = [LEAVE_BUTTON, SETTINGS_BUTTON]

    all_buttons = game_buttons + always_on_buttons

    def is_my_turn() -> bool:
        return current_state.current_turn == Player.player1

    server.start()

    while run:
        clock.tick(config.FRAMERATE)
        screen.fill("black")
        cursor = pygame.SYSTEM_CURSOR_ARROW
        MOUSE_POSITION = pygame.mouse.get_pos()
        GraphicsManager.render_background(screen=screen)

        current_state = server.local_get_game_state()

        backgammon = Backgammon.from_state(current_state)
        player_colors = {
            Player.player1: GameManager.get_setting(SettingsKeys.PIECE_COLOR),
            Player.player2: ColorConverter.pydantic_to_pygame(
                current_state.online_color
            ),
        }
        graphics.render_board(
            game_state=current_state, is_online=True, player_colors=player_colors
        )

        if last_clicked_index == -1:
            if backgammon.get_captured_pieces() > 0:
                highlighted_indexes = backgammon.get_bar_leaving_positions()
            else:
                highlighted_indexes = backgammon.get_movable_pieces()

        graphics.highlight_tracks(highlighted_indexes)

        if (
            not options
            and server.local_is_playing()
            and (
                (
                    is_my_turn()
                    and (
                        graphics.check_track_input(mouse_position=MOUSE_POSITION) != -1
                        or graphics.check_home_track_input(
                            mouse_position=MOUSE_POSITION,
                            player=backgammon.current_turn,
                        )
                    )
                )
                or any(button.check_for_input(MOUSE_POSITION) for button in all_buttons)
            )
        ):
            cursor = pygame.SYSTEM_CURSOR_HAND

        DONE_BUTTON.toggle(disabled=not is_my_turn() or not backgammon.is_turn_done())
        UNDO_BUTTON.toggle(disabled=not backgammon.has_history() or not is_my_turn())

        for button in all_buttons:
            if not server.local_is_alone():
                button.change_color(MOUSE_POSITION)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and not options
                and server.local_is_playing()
            ):
                for button in always_on_buttons:
                    if button.check_for_input(mouse_position=MOUSE_POSITION):
                        button.click()

                if is_my_turn():
                    for button in game_buttons:
                        if button.check_for_input(mouse_position=MOUSE_POSITION):
                            button.click()

                if graphics.check_home_track_input(
                    mouse_position=MOUSE_POSITION, player=backgammon.current_turn
                ):
                    move = Move(
                        move_type=MoveType.bear_off, start=last_clicked_index, end=24
                    )
                    save_state(server.local_move(move=move))
                    last_clicked_index = -1

                index = graphics.check_track_input(mouse_position=MOUSE_POSITION)
                if index != -1:  # clicked on track
                    if (
                        last_clicked_index == -1
                        and backgammon.get_captured_pieces() == 0
                    ):  # clicked on a movable piece
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
                            save_state(server.local_move(move=move))

                        else:
                            move = Move(
                                move_type=MoveType.normal_move,
                                start=last_clicked_index,
                                end=index,
                            )
                            save_state(server.local_move(move=move))

                        # a piece had been moved
                        last_clicked_index = -1
                        highlighted_indexes = backgammon.get_movable_pieces()

                    print(last_clicked_index)

        if server.local_is_alone():
            close_options()
            render_waiting(screen=screen, leave=leave_button_click)
        elif options:
            options_menu(screen=screen, close=close_options)
        else:
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

    if LEAVE_BUTTON.check_for_input(MOUSE_POSITION):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and LEAVE_BUTTON.check_for_input(
            mouse_position=MOUSE_POSITION
        ):
            LEAVE_BUTTON.click()
