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
from models.game_state import OnlineGameState, ColorConverter, local_to_online
from models.move import Move, MoveType
from server.server import Network, ServerFlags
from game_manager import SettingsKeys, GameManager


def online_client(screen: pygame.Surface, clock: pygame.time.Clock, ip_address: str):
    run = True
    options = False
    graphics = GraphicsManager(screen=screen)

    def open_options():
        nonlocal options
        options = True

    def close_options():
        nonlocal options
        options = False

    refresh_frequency = 500  # in milliseconds

    piece_color = GameManager.get_setting(SettingsKeys.PIECE_COLOR)
    current_state: OnlineGameState = local_to_online(
        game_state=Backgammon().get_state(),
        online_color=ColorConverter.pygame_to_pydantic(piece_color),
        local_color=ColorConverter.pygame_to_pydantic(piece_color),
    )
    started = False

    network = Network(
        ip_address=ip_address,
        port=config.GAME_PORT,
        buffer_size=config.NETWORK_BUFFER,
        timeout=10,
    )

    def save_state(state: OnlineGameState):
        nonlocal current_state
        current_state = state

        nonlocal started
        if not started:
            started = True

    def send_color():
        network.send(
            data=ColorConverter.pygame_to_pydantic(piece_color),
            callback=save_state,
        )
        print("Sent data to server")

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

    def is_reconnecting() -> bool:
        return not network.got_last_send and network.is_trying_to_connect()

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

    DONE_BUTTON.toggle(disabled=True)
    UNDO_BUTTON.toggle(disabled=True)

    game_buttons = [DONE_BUTTON, UNDO_BUTTON]
    always_on_buttons = [LEAVE_BUTTON, SETTINGS_BUTTON]

    all_buttons = game_buttons + always_on_buttons

    def is_my_turn() -> bool:
        return current_state.current_turn == Player.player1

    time = pygame.time.get_ticks()

    while run:
        clock.tick(config.FRAMERATE)
        screen.fill("black")
        cursor = pygame.SYSTEM_CURSOR_ARROW
        MOUSE_POSITION = pygame.mouse.get_pos()

        GraphicsManager.render_background(screen=screen)

        opponent_color = ColorConverter.pydantic_to_pygame(current_state.local_color)

        while piece_color == opponent_color:
            piece_color = pygame.Color(
                255 - opponent_color.r, 255 - opponent_color.g, 255 - opponent_color.b
            )
        player_colors = {
            Player.player1: piece_color,
            Player.player2: opponent_color,
        }

        graphics.render_board(
            game_state=current_state, is_online=True, player_colors=player_colors
        )

        if (
            pygame.time.get_ticks() - time > refresh_frequency
            and started
            and network.got_last_send
        ):
            time = pygame.time.get_ticks()
            send_color()

        backgammon = Backgammon.from_state(current_state)

        if last_clicked_index == -1:
            if backgammon.get_captured_pieces() > 0:
                highlighted_indexes = backgammon.get_bar_leaving_positions()
            else:
                highlighted_indexes = backgammon.get_movable_pieces()

        graphics.highlight_tracks(highlighted_indexes)

        if (
            not options
            and (
                is_my_turn()
                and (
                    graphics.check_track_input(mouse_position=MOUSE_POSITION) != -1
                    or graphics.check_home_track_input(
                        mouse_position=MOUSE_POSITION, player=backgammon.current_turn
                    )
                )
            )
            or any(button.check_for_input(MOUSE_POSITION) for button in all_buttons)
        ):
            cursor = pygame.SYSTEM_CURSOR_HAND

        DONE_BUTTON.toggle(disabled=not is_my_turn() or not backgammon.is_turn_done())
        UNDO_BUTTON.toggle(disabled=not backgammon.has_history() or not is_my_turn())

        for button in all_buttons:
            if not options and not is_reconnecting():
                button.change_color(MOUSE_POSITION)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN and not options and is_my_turn():
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
                    network.send(data=move, callback=save_state)
                    last_clicked_index = -1

                index = graphics.check_track_input(mouse_position=MOUSE_POSITION)
                if index != -1:
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
                        last_clicked_index = -1
                        highlighted_indexes = backgammon.get_movable_pieces()

                    print(last_clicked_index)

        if is_reconnecting():
            render_connecting(screen=screen)
            if not network.connected:
                run = False
        elif options:
            options_menu(screen=screen, close=close_options)
        else:
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

    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    CONNECTING_TEXT_RECT = CONNECTING.get_rect(center=(get_mid_width(), 300))

    screen.blit(CONNECTING, CONNECTING_TEXT_RECT)
