import time
from typing import Callable
from pygame import Surface
import pygame
from pygame.event import Event
from pygame.time import Clock
from backgammon import Backgammon
from backgammon import BackgammonAI
import config
from game_manager import GameManager
from graphics.elements import ButtonElement, TimerElement
from graphics.graphics_manager import GraphicsManager
from menus.menus import ConnectingMenu, LostConnectionMenu, UnfocusedMenu, WaitingMenu
from menus.screen import GameScreen, GameScreenElementKeys
from menus.menus import OptionsMenu
from models import ColorConverter, GameState, Move, MoveType, OnlineGameState, ScoredMoves, ServerFlags
from models import Player
from network import BGServer, NetworkClient


class BotGame(GameScreen):

    @classmethod
    def start(cls, screen: Surface, clock: Clock):
        cls.run = True
        cls.last_clicked_index = -1
        cls.options = False
        cls.bot = False
        cls.graphics = GraphicsManager(screen=screen)
        cls.backgammon = Backgammon()

        cls.set_up_elements()

        cls.play_next_turn_sounds()

        if not cls.is_my_turn():
            print("hello")
            cls.setup_bot()

        while cls.run:
            clock.tick(config.FRAMERATE)
            cursor = pygame.SYSTEM_CURSOR_ARROW
            GraphicsManager.render_background(screen=screen)

            cls.render_board(is_online=True)

            if cls.bot and time.time() - cls.bot_current_time > 1:
                cls.move_bot(on_game_over=cls.done_turn)

            events = pygame.event.get()

            cls.check_quit(events=events, quit=GameManager.quit)

            cls.render_elements(
                screen=screen,
                elements=cls.all_elements,
                events=events,
                update_condition=not cls.is_screen_on_top(),
            )

            cls.update_game_buttons()
            cls.highlight_tracks()

            if not cls.is_screen_on_top():
                cursor = cls.get_cursor(elements=cls.always_on_buttons)

                cls.click_elements(elements=cls.always_on_buttons, events=events)

            if not cls.is_screen_on_top() and cls.is_my_turn():

                cursor = cls.get_cursor(elements=cls.all_elements)

                cls.click_elements(elements=cls.game_buttons, events=events)

                cls.move_piece(events=events)

            if not GameManager.is_window_focused():
                UnfocusedMenu.start(screen=screen)
            elif cls.options:
                OptionsMenu.start(screen=screen, close=cls.close_options, events=events)
            else:
                pygame.mouse.set_cursor(cursor)

            pygame.display.flip()

    @classmethod
    def is_my_turn(cls) -> bool:
        return Player.player1 == cls.backgammon.current_turn

    @classmethod
    def is_screen_on_top(cls):
        return cls.options or not GameManager.is_window_focused()

    @classmethod
    def open_options(cls):
        cls.timer.stop()
        cls.options = True

    @classmethod
    def close_options(cls):
        cls.timer.start()
        cls.options = False

    @classmethod
    def stop(cls):
        cls.run = False

    @classmethod
    def done_turn(cls):
        cls.last_clicked_index = -1
        cls.play_next_turn_sounds()

        if cls.backgammon.is_game_over():
            cls.backgammon.new_game(cls.backgammon.winner)
            if not cls.is_my_turn():
                cls.setup_bot()
            return

        cls.backgammon.switch_turn()
        print(f"is bot turn: {cls.is_my_turn()}")
        if not cls.is_my_turn():
            cls.setup_bot()

    @classmethod
    def on_random_click(cls):
        cls.last_clicked_index = -1
        print(cls.is_my_turn())

    @classmethod
    def has_history(cls):
        return cls.backgammon.has_history()
    
    @classmethod
    def on_normal_move(cls, clicked_index: int):
        cls.backgammon.make_move(start=cls.last_clicked_index, end=clicked_index)
        cls.last_clicked_index = -1

    @classmethod
    def on_leave_bar(cls, clicked_index: int):
        cls.backgammon.leave_bar(end=clicked_index)
        cls.last_clicked_index = -1

    @classmethod
    def on_bear_off(cls):
        cls.backgammon.bear_off(start=cls.last_clicked_index)
        cls.last_clicked_index = -1

    @classmethod
    def on_choose_piece(cls, clicked_index: int):
        cls.last_clicked_index = clicked_index

    @classmethod
    def undo_move(cls):
        cls.backgammon.undo()


class OfflineGame(GameScreen):

    @classmethod
    def start(cls, screen: Surface, clock: Clock):
        cls.run = True
        cls.graphics = GraphicsManager(screen=screen)
        cls.backgammon = Backgammon()
        cls.last_clicked_index = -1
        cls.options = False
        cls.bot = False

        cls.set_up_elements()

        cls.play_next_turn_sounds()

        while cls.run:
            clock.tick(config.FRAMERATE)
            cursor = pygame.SYSTEM_CURSOR_ARROW
            GraphicsManager.render_background(screen=screen)

            if cls.bot and time.time() - cls.bot_current_time > 1:
                cls.move_bot(on_game_over=cls.done_turn)

            cls.render_board()

            cls.update_game_buttons()

            events = pygame.event.get()
            cls.check_quit(events=events, quit=GameManager.quit)

            cls.render_elements(
                screen=screen,
                elements=cls.all_elements,
                update_condition=not cls.is_screen_on_top(),
                events=events,
            )

            cls.highlight_tracks()

            if not cls.is_screen_on_top():

                cursor = cls.get_cursor(elements=cls.all_elements)

                cls.click_elements(elements=cls.all_elements, events=events)

                cls.move_piece(events=events)

            if not GameManager.is_window_focused():
                UnfocusedMenu.start(screen=screen)
            elif cls.options:
                OptionsMenu.start(screen=screen, close=cls.close_options, events=events)
            else:
                pygame.mouse.set_cursor(cursor)

            pygame.display.flip()

    @classmethod
    def is_my_turn(cls):
        return True

    @classmethod
    def open_options(cls):
        cls.timer.stop()
        cls.options = True

    @classmethod
    def close_options(cls):
        cls.timer.start()
        cls.options = False

    @classmethod
    def stop(cls):
        cls.run = False

    @classmethod
    def done_turn(cls):
        cls.last_clicked_index = -1
        cls.play_next_turn_sounds()
        if cls.backgammon.is_game_over():
            cls.backgammon.new_game(cls.backgammon.winner)
            return

        cls.backgammon.switch_turn()

    @classmethod
    def on_random_click(cls):
        cls.last_clicked_index = -1

    @classmethod
    def on_normal_move(cls, clicked_index: int):
        cls.backgammon.make_move(start=cls.last_clicked_index, end=clicked_index)
        cls.last_clicked_index = -1

    @classmethod
    def on_leave_bar(cls, clicked_index: int):
        cls.backgammon.leave_bar(end=clicked_index)
        cls.last_clicked_index = -1

    @classmethod
    def on_bear_off(cls):
        cls.backgammon.bear_off(start=cls.last_clicked_index)
        cls.last_clicked_index = -1

    @classmethod
    def on_choose_piece(cls, clicked_index: int):
        cls.last_clicked_index = clicked_index

    @classmethod
    def is_screen_on_top(cls):
        return cls.options or not GameManager.is_window_focused()

    @classmethod
    def undo_move(cls):
        cls.backgammon.undo()
    
    @classmethod
    def has_history(cls):
        return cls.backgammon.has_history()

class LocalClientGame(GameScreen):

    @classmethod
    def start(cls, screen: Surface, clock: Clock):
        cls.run = True
        cls.options = False
        cls.bot = False
        cls.graphics = GraphicsManager(screen=screen)

        cls.server = BGServer(
            port=config.GAME_PORT,
            buffer_size=config.NETWORK_BUFFER,
            local_color=GameManager.options.player_colors[Player.player1],
            online_color=GameManager.options.player_colors[Player.player2],
        )
        cls.online_state = cls.server.local_get_game_state()
        cls.online_state.current_turn = Player.other(cls.online_state.current_turn)
        cls.backgammon = Backgammon([cls.online_state])

        cls.last_clicked_index = -1

        cls.highlighted_indexes = []

        cls.set_up_elements()

        cls.server.run_server()

        while cls.run:
            clock.tick(config.FRAMERATE)
            cursor = pygame.SYSTEM_CURSOR_ARROW
            GraphicsManager.render_background(screen=screen)

            if cls.bot and time.time() - cls.bot_current_time > 1:
                cls.move_bot(on_move=cls.on_bot_move)

            cls.save_state(state=cls.server.local_get_game_state())

            cls.render_board(
                is_online=True,
                opponent_color=ColorConverter.pydantic_to_pygame(
                    cls.online_state.online_color
                ),
            )

            cls.update_game_buttons()

            cls.highlight_tracks(is_my_turn=cls.is_my_turn())

            events = pygame.event.get()

            cls.check_quit(events=events, quit=cls.quit)

            cls.timer.update(events)

            cls.render_elements(
                screen=screen,
                elements=cls.all_elements,
                update_condition=not cls.is_screen_on_top(),
                events=events,
            )

            if not cls.is_screen_on_top():

                cursor = cls.get_cursor(elements=cls.always_on_buttons)

                cls.click_elements(elements=cls.always_on_buttons, events=events)

            if not cls.is_screen_on_top() and cls.is_my_turn():
                cursor = cls.get_cursor(elements=cls.all_elements)
                cls.click_elements(elements=cls.game_buttons, events=events)

                cls.move_piece(events=events)

            if not cls.server.connected:
                cls.timer.stop()
                WaitingMenu.start(screen=screen, close=cls.stop, events=events)
            elif not GameManager.is_window_focused():
                UnfocusedMenu.start(screen=screen)
            elif cls.options:
                OptionsMenu.start(screen=screen, close=cls.close_options, events=events)
            else:
                pygame.mouse.set_cursor(cursor)

            pygame.display.flip()

    @classmethod
    def save_state(cls, state: OnlineGameState):
        if not cls.server.game_started:
            return

        p1 = Player.player1
        p2 = Player.player2

        if (
            state.current_turn != cls.backgammon.current_turn
            or state.score[p2] + state.score[p1]
            != cls.backgammon.score[p2] + cls.backgammon.score[p1]
        ):
            cls.play_next_turn_sounds()
            
        if not cls.online_state.is_board_equal(state=state):
            cls.play_piece_sound()
        
        cls.online_state = state
        cls.backgammon = Backgammon([state])

    @classmethod
    def has_history(cls):
        return cls.online_state.history_length > 0
    
    @classmethod
    def is_my_turn(cls):
        return cls.backgammon.current_turn == Player.player1

    @classmethod
    def stop(cls):
        cls.server.stop_server()
        cls.run = False

    @classmethod
    def done_turn(cls):
        cls.last_clicked_index = -1
        cls.save_state(state=cls.server.done_turn())

    @classmethod
    def on_random_click(cls):
        cls.last_clicked_index = -1

    @classmethod
    def on_normal_move(cls, clicked_index: int):
        move = Move(
            move_type=MoveType.normal_move,
            start=cls.last_clicked_index,
            end=clicked_index,
        )
        cls.save_state(state=cls.server.move_piece(move=move))
        cls.last_clicked_index = -1

    @classmethod
    def on_leave_bar(cls, clicked_index: int):
        move = Move(
            move_type=MoveType.leave_bar,
            start=cls.backgammon.get_start_position(),
            end=clicked_index,
        )
        cls.save_state(state=cls.server.move_piece(move=move))
        cls.last_clicked_index = -1

    @classmethod
    def on_bear_off(cls):
        move = Move(
            move_type=MoveType.bear_off,
            start=cls.last_clicked_index,
            end=24,
        )
        cls.save_state(state=cls.server.move_piece(move=move))
        cls.last_clicked_index = -1

    @classmethod
    def on_choose_piece(cls, clicked_index: int):
        cls.last_clicked_index = clicked_index

    @classmethod
    def on_bot_move(cls, move: Move):
        cls.save_state(state=cls.server.move_piece(move))

    @classmethod
    def is_screen_on_top(cls):
        return (
            cls.options
            or not GameManager.is_window_focused()
            or not cls.server.connected
        )

    @classmethod
    def undo_move(cls):
        cls.save_state(cls.server.undo_move())

    @classmethod
    def quit(cls):
        cls.stop()
        GameManager.quit()


class OnlineClientGame(GameScreen):

    @classmethod
    def start(cls, screen: Surface, clock: Clock, ip_address: str):
        cls.run = True
        cls.options = False
        cls.started = False
        cls.bot = False
        cls.timeout = 10
        cls.graphics = GraphicsManager(screen=screen)

        cls.refresh_frequency = 0.5  # in seconds

        piece_color = GameManager.options.player_colors[Player.player1]
        opponent_color = GameManager.options.player_colors[Player.player2]

        cls.backgammon = Backgammon()
        cls.online_state = OnlineGameState(
            **cls.backgammon.state.model_dump(),
            history_length=0,
            online_color=piece_color,
            local_color=opponent_color,
        )

        cls.network_client = NetworkClient(
            host_ip=ip_address,
            port=config.GAME_PORT,
            buffer_size=config.NETWORK_BUFFER,
            timeout=cls.timeout,
        )

        cls.network_client.connect()

        cls.last_clicked_index = -1

        cls.highlighted_indexes = []

        cls.set_up_elements()

        cls.bot_current_time = time.time()
        
        cls.game_time = time.time()

        while cls.run:
            clock.tick(config.FRAMERATE)
            screen.fill("black")
            cursor = pygame.SYSTEM_CURSOR_ARROW

            GraphicsManager.render_background(screen=screen)

            if cls.bot and time.time() - cls.bot_current_time > 1:
                cls.move_bot(on_move=cls.on_bot_move)
            
            opponent_color = ColorConverter.pydantic_to_pygame(
                cls.online_state.local_color
            )
            cls.render_board(is_online=True, opponent_color=opponent_color)

            if time.time() - cls.game_time > cls.refresh_frequency:
                cls.game_time = time.time()
                cls.send_color()

            cls.update_game_buttons()
            
            cls.highlight_tracks(is_my_turn=cls.is_my_turn())

            events = pygame.event.get()
            
            cls.check_quit(events=events, quit=cls.quit)

            cls.timer.update(events)

            cls.render_elements(
                screen=screen,
                elements=cls.all_elements,
                events=events,
                update_condition=not cls.is_screen_on_top(),
            )

            if not cls.is_screen_on_top():

                cursor = cls.get_cursor(elements=cls.always_on_buttons)

                cls.click_elements(elements=cls.always_on_buttons, events=events)

            if not cls.is_screen_on_top() and cls.is_my_turn():

                cursor = cls.get_cursor(elements=cls.all_elements)

                cls.move_piece(events=events)

                cls.click_elements(elements=cls.game_buttons, events=events)

            if (
                not cls.network_client.connected
                and cls.network_client.started
            ):
                cls.timer.stop()
                LostConnectionMenu.start(screen=screen, close=cls.stop, events=events)
            elif not cls.network_client.started or cls.is_reconnecting():
                ConnectingMenu.start(screen=screen)
                if not cls.network_client.connected:
                    cls.run = False
            elif not GameManager.is_window_focused():
                UnfocusedMenu.start(screen=screen)
            elif cls.options:
                OptionsMenu.start(screen=screen, close=cls.close_options, events=events)
            else:
                pygame.mouse.set_cursor(cursor)

            pygame.display.flip()

    @classmethod
    def has_history(cls):
        return cls.online_state.history_length > 0
    
    
    @classmethod
    def on_bot_move(cls, move: Move):
        cls.network_client.send(data=move, on_recieve=cls.save_state)
    
    @classmethod
    def on_random_click(cls):
        cls.last_clicked_index = -1

    @classmethod
    def on_normal_move(cls, clicked_index: int):
        move = Move(
            move_type=MoveType.normal_move,
            start=cls.last_clicked_index,
            end=clicked_index,
        )
        cls.network_client.send(data=move, on_recieve=cls.save_state)
        cls.last_clicked_index = -1

    @classmethod
    def on_leave_bar(cls, clicked_index: int):
        move = Move(
            move_type=MoveType.leave_bar,
            start=cls.backgammon.get_start_position(),
            end=clicked_index,
        )
        cls.network_client.send(data=move, on_recieve=cls.save_state)
        cls.last_clicked_index = -1

    @classmethod
    def on_bear_off(cls):
        move = Move(move_type=MoveType.bear_off, start=cls.last_clicked_index, end=24)
        cls.network_client.send(data=move, on_recieve=cls.save_state)
        cls.last_clicked_index = -1

    @classmethod
    def on_choose_piece(cls, clicked_index: int):
        cls.last_clicked_index = clicked_index

    @classmethod
    def stop(cls):
        cls.network_client.disconnect(data=ServerFlags.leave)
        cls.run = False

    @classmethod
    def done_turn(cls):
        cls.network_client.send(data=ServerFlags.done, on_recieve=cls.save_state)

    @classmethod
    def undo_move(cls):
        cls.network_client.send(data=ServerFlags.undo, on_recieve=cls.save_state)

    @classmethod
    def is_screen_on_top(cls):
        return (
            cls.options or not GameManager.is_window_focused() or cls.is_reconnecting()
        )

    @classmethod
    def is_reconnecting(cls):
        return cls.network_client.time_from_last_recieve > cls.timeout / 2

    @classmethod
    def save_state(cls, state: OnlineGameState):
        p1 = Player.player1
        p2 = Player.player2

        if (
            not cls.started
            or state.current_turn != cls.online_state.current_turn
            or state.score[p2] + state.score[p1]
            != cls.online_state.score[p2] + cls.online_state.score[p1]
        ):
            cls.play_next_turn_sounds()

        if not cls.online_state.is_board_equal(state=state):
            cls.play_piece_sound()
        
        cls.online_state = state
        cls.backgammon = Backgammon([state])
        cls.started = True

    @classmethod
    def send_color(cls):
        cls.network_client.send(
            data=GameManager.options.player_colors[Player.player1],
            on_recieve=cls.save_state,
        )

    @classmethod
    def quit(cls):
        cls.stop()
        GameManager.quit()

    @classmethod
    def is_my_turn(cls) -> bool:
        return cls.backgammon.current_turn == Player.player1
