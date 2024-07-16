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
from models.game_state import GameState
from models.move import Move, MoveType
from server.server import Network, ServerFlags


def online_client(screen: pygame.Surface, clock: pygame.time.Clock, ip_address: str):
    run = True
    player1_color = pygame.Color(100, 100, 100)
    player2_color = pygame.Color(150, 100, 100)
    graphics = GraphicsManager(
        screen=screen, player1_color=player1_color, player2_color=player2_color
    )

    refresh_frequency = 1000
    time = pygame.time.get_ticks()

    current_state: GameState = Backgammon().get_state()
    started = False

    network = Network(
        ip_address=ip_address, port=config.GAME_PORT, buffer_size=config.NETWORK_BUFFER, timeout=10
    )

    def save_state(state: GameState):
        nonlocal current_state
        current_state = state

        nonlocal started
        started = True

    network.connect(save_state)

    last_clicked_index = -1

    def get_movable_pieces():
        return Backgammon.from_state(current_state).get_movable_pieces()

    def leave_button_click():
        network.send(data=ServerFlags.LEAVE)
        network.close()
        nonlocal run
        run = False

    def done_button_click():
        network.send(data=ServerFlags.DONE, callback=save_state)

    def undo_button_click():
        network.send(data=ServerFlags.UNDO, callback=save_state)

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

    DONE_BUTTON.toggle(disabled=True)
    UNDO_BUTTON.toggle(disabled=True)

    game_buttons = [DONE_BUTTON, UNDO_BUTTON, LEAVE_BUTTON, SETTINGS_BUTTON]

    def is_my_turn() -> bool:
        return current_state.current_turn == Player.player2

    while run:
        clock.tick(config.FRAMERATE)
        screen.fill("black")
        cursor = pygame.SYSTEM_CURSOR_ARROW
        MOUSE_POSITION = pygame.mouse.get_pos()

        GraphicsManager.render_background(screen=screen)

        if (
            pygame.time.get_ticks() - time > refresh_frequency
            and started
            and network.got_last_send
        ):
            time = pygame.time.get_ticks()
            network.send(data=ServerFlags.GET_GAME_STATE, callback=save_state)

        backgammon = Backgammon.from_state(current_state)

        if last_clicked_index == -1:
            if backgammon.get_captured_pieces() > 0:
                highlighted_indexes = backgammon.get_bar_leaving_positions()
            else:
                highlighted_indexes = backgammon.get_movable_pieces()

        graphics.render_board(current_state)

        graphics.highlight_tracks(highlighted_indexes)
        if (
            is_my_turn()
            and (
                graphics.check_tracks_input(mouse_position=MOUSE_POSITION)
                or graphics.check_home_track_input(
                    mouse_position=MOUSE_POSITION, player=backgammon.current_turn
                )
            )
        ) or any(button.check_for_input(MOUSE_POSITION) for button in game_buttons):
            cursor = pygame.SYSTEM_CURSOR_HAND

        DONE_BUTTON.toggle(disabled=not is_my_turn() or not backgammon.is_turn_done())
        UNDO_BUTTON.toggle(disabled=not backgammon.has_history() or not is_my_turn())

        for button in game_buttons:
            button.change_color(MOUSE_POSITION)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN and LEAVE_BUTTON.check_for_input(
                MOUSE_POSITION
            ):
                LEAVE_BUTTON.click()

            if event.type == pygame.MOUSEBUTTONDOWN and is_my_turn():

                for button in game_buttons:
                    if button.check_for_input(mouse_position=MOUSE_POSITION):
                        button.click()

                did_hit_target = False
                if graphics.check_home_track_input(
                    mouse_position=MOUSE_POSITION, player=backgammon.current_turn
                ):
                    move = Move(
                        move_type=MoveType.bear_off, start=last_clicked_index, end=24
                    )
                    network.send(data=move, callback=save_state)

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
                                network.send(data=move, callback=save_state)

                            else:
                                move = Move(
                                    move_type=MoveType.normal_move,
                                    start=last_clicked_index,
                                    end=index,
                                )
                                network.send(data=move, callback=save_state)

                            # a piece had been moved
                            highlighted_indexes = backgammon.get_movable_pieces()
                            last_clicked_index = -1

                last_clicked_index = -1 if not did_hit_target else last_clicked_index
                print(last_clicked_index)

        if not network.got_last_send and network.is_trying_to_connect():
            render_connecting(screen=screen)
            if not network.connected:
                run = False

        pygame.mouse.set_cursor(cursor)
        pygame.display.flip()


def render_connecting(screen: pygame.Surface) -> None:
    menu_surface = pygame.Surface(
        size=config.RESOLUTION, flags=pygame.SRCALPHA, depth=32
    )
    menu_surface.convert_alpha()
    menu_surface.fill(pygame.Color(0, 0, 0, 180))
    screen.blit(source=menu_surface, dest=(0, 0))

    CONNECTING = OutlineText.render(
        text="RECONNECTING...",
        font=get_font(100),
        gfcolor=pygame.Color("white"),
        ocolor=pygame.Color("black"),
        opx=3,
    )

    CONNECTING_TEXT_RECT = CONNECTING.get_rect(center=(get_mid_width(), 300))

    screen.blit(CONNECTING, CONNECTING_TEXT_RECT)
