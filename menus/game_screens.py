import math
from pygame import Surface
import pygame
from pygame.time import Clock
from backgammon import Backgammon
from backgammon import BackgammonAI
import config
from game_manager import GameManager, SettingsKeys
from graphics.buttons import Button
from graphics.graphics_manager import ColorConverter, GraphicsManager, get_font
from menus.menus import OptionsMenu, ReconnectingMenu, UnfocusedMenu, WaitingMenu
from menus.screen import GameScreen, GameScreenButtonKeys
from models import GameState, Move, MoveType, OnlineGameState, ScoredMoves
from models import Player
from server import BGServer, Network, ServerFlags


class BotGame(GameScreen):

    @classmethod
    def start(cls, screen: Surface, clock: Clock):
        run = True
        options = False
        time = pygame.time.get_ticks()
        ai_moves: list[Move] = []
        graphics = GraphicsManager(screen=screen)
        ai_got_moves = False
        backgammon = Backgammon()

        last_clicked_index = -1
        bot_player = Player.player2

        def is_bot_turn() -> bool:
            return bot_player == backgammon.current_turn

        def is_screen_on_top():
            nonlocal options
            return options or not GameManager.is_window_focused()

        def bot_turn():
            def save_ai_moves(scored_moves: ScoredMoves):
                nonlocal ai_got_moves
                ai_got_moves = True
                nonlocal ai_moves
                ai_moves = scored_moves.moves
                print(ai_moves)

            BackgammonAI.get_best_move(game=backgammon, callback=save_ai_moves)

        highlighted_indexes = []

        if is_bot_turn():
            bot_turn()
        else:
            highlighted_indexes = backgammon.get_movable_pieces()

        def leave_button_click():
            nonlocal run
            run = False

        def done_button_click():
            if backgammon.is_game_over():
                winner = backgammon.get_winner()
                print(winner)
                backgammon.set_winning_score(winner)
                backgammon.new_game(winner)
                if is_bot_turn():
                    bot_turn()
                return

            backgammon.switch_turn()
            nonlocal time
            time = pygame.time.get_ticks()
            bot_turn()

        def undo_button_click():
            backgammon.undo()
            nonlocal highlighted_indexes
            highlighted_indexes = backgammon.get_movable_pieces()

        def open_options():
            nonlocal options
            options = True

        def close_options():
            nonlocal options
            options = False

        buttons_dict = cls._get_buttons(
            on_leave=leave_button_click,
            on_done=done_button_click,
            on_options=open_options,
            on_undo=undo_button_click,
            graphics=graphics,
        )

        buttons = [buttons_dict[key] for key in buttons_dict]

        def on_random_click():
            nonlocal last_clicked_index
            last_clicked_index = -1

        def on_normal_move(clicked_index: int):
            backgammon.make_move(start=last_clicked_index, end=clicked_index)
            on_random_click()

        def on_leave_bar(clicked_index: int):
            backgammon.leave_bar(end=clicked_index)
            on_random_click()

        def on_bear_off(clicked_index: int):
            backgammon.bear_off(start=clicked_index)
            on_random_click()

        def on_choose_piece(clicked_index: int):
            nonlocal last_clicked_index
            last_clicked_index = clicked_index

            nonlocal highlighted_indexes
            highlighted_indexes = backgammon.get_possible_tracks(start=clicked_index)

        while run:
            clock.tick(config.FRAMERATE)
            screen.fill("black")
            cursor = pygame.SYSTEM_CURSOR_ARROW
            GraphicsManager.render_background(screen=screen)

            player_colors = {
                Player.player1: GameManager.get_setting(SettingsKeys.PIECE_COLOR),
                Player.player2: GameManager.get_setting(SettingsKeys.OPPONENT_COLOR),
            }
            graphics.render_board(
                game_state=backgammon.get_state(),
                is_online=True,
                player_colors=player_colors,
            )

            if is_bot_turn() and ai_got_moves and pygame.time.get_ticks() - time > 1000:
                time = pygame.time.get_ticks()
                if len(ai_moves) == 0:
                    ai_got_moves = False
                    print("bot played")
                    if backgammon.is_game_over():
                        done_button_click()
                        continue
                    backgammon.switch_turn()
                else:
                    move = ai_moves.pop()
                    backgammon.handle_move(move=move)

            if (
                last_clicked_index == -1
                and not is_bot_turn()
                and not is_screen_on_top()
            ):
                highlighted_indexes = cls._get_highlighted_tracks(
                    graphics=graphics, backgammon=backgammon
                )

            graphics.highlight_tracks(highlighted_indexes)

            buttons_dict[GameScreenButtonKeys.DONE].toggle(
                disabled=not backgammon.is_turn_done() or is_bot_turn()
            )
            buttons_dict[GameScreenButtonKeys.UNDO].toggle(
                disabled=not backgammon.has_history() or is_bot_turn()
            )

            cursor = cls.get_cursor(
                graphics=graphics,
                buttons=buttons,
                backgammon=backgammon,
                condition=not is_screen_on_top(),
            )

            cls._check_buttons(
                screen=screen, buttons=buttons, condition=not is_screen_on_top()
            )

            for event in pygame.event.get():
                cls._check_quit(event=event, quit=GameManager.quit)
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and not is_bot_turn()
                    and not is_screen_on_top()
                ):
                    cls._click_buttons(buttons=buttons)

                    cls._move_piece(
                        graphics=graphics,
                        backgammon=backgammon,
                        last_clicked_index=last_clicked_index,
                        on_random_click=on_random_click,
                        on_normal_move=on_normal_move,
                        on_leave_bar=on_leave_bar,
                        on_choose_piece=on_choose_piece,
                        on_bear_off=on_bear_off,
                    )

            if not GameManager.is_window_focused():
                UnfocusedMenu.start(screen=screen)
            elif options:
                OptionsMenu.start(screen=screen, close=close_options)
            else:
                pygame.mouse.set_cursor(cursor)

            pygame.display.flip()


class OfflineGame(GameScreen):

    @classmethod
    def start(cls, screen: Surface, clock: Clock):
        run = True
        options = False
        graphics = GraphicsManager(screen=screen)
        backgammon = Backgammon()
        last_clicked_index = -1

        def is_screen_on_top():
            nonlocal options
            return options or not GameManager.is_window_focused()

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
            buttons_dict[GameScreenButtonKeys.DONE].toggle()

        def undo_button_click():
            backgammon.undo()
            nonlocal highlighted_indexes
            highlighted_indexes = backgammon.get_movable_pieces()

        highlighted_indexes = backgammon.get_movable_pieces()

        buttons_dict = cls._get_buttons(
            on_leave=leave_button_click,
            on_done=done_button_click,
            on_options=open_options,
            on_undo=undo_button_click,
            graphics=graphics,
        )

        buttons = [buttons_dict[key] for key in buttons_dict]

        def on_random_click():
            nonlocal last_clicked_index
            last_clicked_index = -1

        def on_normal_move(clicked_index: int):
            backgammon.make_move(start=last_clicked_index, end=clicked_index)
            on_random_click()

        def on_leave_bar(clicked_index: int):
            backgammon.leave_bar(end=clicked_index)
            on_random_click()

        def on_bear_off(clicked_index: int):
            backgammon.bear_off(start=clicked_index)
            on_random_click()

        def on_choose_piece(clicked_index: int):
            nonlocal last_clicked_index
            last_clicked_index = clicked_index

            nonlocal highlighted_indexes
            highlighted_indexes = backgammon.get_possible_tracks(start=clicked_index)

        while run:
            clock.tick(config.FRAMERATE)
            screen.fill("black")
            cursor = pygame.SYSTEM_CURSOR_ARROW
            MOUSE_POSITION = pygame.mouse.get_pos()

            GraphicsManager.render_background(screen=screen)

            player_colors = {
                Player.player1: GameManager.get_setting(SettingsKeys.PIECE_COLOR),
                Player.player2: GameManager.get_setting(SettingsKeys.OPPONENT_COLOR),
            }

            graphics.render_board(
                game_state=backgammon.get_state(), player_colors=player_colors
            )

            if last_clicked_index == -1:
                highlighted_indexes = cls._get_highlighted_tracks(
                    graphics=graphics, backgammon=backgammon
                )

            graphics.highlight_tracks(highlighted_indexes)

            cursor = cls.get_cursor(
                graphics=graphics,
                buttons=buttons,
                backgammon=backgammon,
                condition=not is_screen_on_top(),
            )

            buttons_dict[GameScreenButtonKeys.DONE].toggle(
                disabled=not backgammon.is_turn_done()
            )
            buttons_dict[GameScreenButtonKeys.UNDO].toggle(
                disabled=not backgammon.has_history()
            )

            cls._check_buttons(
                screen=screen, buttons=buttons, condition=not is_screen_on_top()
            )

            for event in pygame.event.get():
                cls._check_quit(event=event, quit=GameManager.quit)
                if event.type == pygame.MOUSEBUTTONDOWN and not is_screen_on_top():

                    cls._click_buttons(buttons=buttons)

                    cls._move_piece(
                        graphics=graphics,
                        backgammon=backgammon,
                        last_clicked_index=last_clicked_index,
                        on_random_click=on_random_click,
                        on_normal_move=on_normal_move,
                        on_leave_bar=on_leave_bar,
                        on_choose_piece=on_choose_piece,
                        on_bear_off=on_bear_off,
                    )

            if not GameManager.is_window_focused():
                UnfocusedMenu.start(screen=screen)
            elif options:
                OptionsMenu.start(screen=screen, close=close_options)
            else:
                pygame.mouse.set_cursor(cursor)

            pygame.display.flip()


class LocalClientGame(GameScreen):

    @classmethod
    def start(cls, screen: Surface, clock: Clock):
        run = True
        options = False
        graphics = GraphicsManager(screen=screen)

        def is_screen_on_top():
            nonlocal options
            return options or not GameManager.is_window_focused() or server.local_is_alone()

        server = BGServer(
            port=config.GAME_PORT,
            buffer_size=config.NETWORK_BUFFER,
            local_color=ColorConverter.pygame_to_pydantic(
                GameManager.get_setting(SettingsKeys.PIECE_COLOR)
            ),
            online_color=ColorConverter.pygame_to_pydantic(
                GameManager.get_setting(SettingsKeys.OPPONENT_COLOR)
            ),
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
            buttons_dict[GameScreenButtonKeys.DONE].toggle()
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

        buttons_dict = cls._get_buttons(
            on_leave=leave_button_click,
            on_done=done_button_click,
            on_options=open_options,
            on_undo=undo_button_click,
            graphics=graphics,
        )

        all_buttons = [buttons_dict[key] for key in buttons_dict]

        game_buttons = [
            buttons_dict[GameScreenButtonKeys.DONE],
            buttons_dict[GameScreenButtonKeys.UNDO],
        ]
        always_on_buttons = [
            buttons_dict[GameScreenButtonKeys.LEAVE],
            buttons_dict[GameScreenButtonKeys.OPTIONS],
        ]

        def is_my_turn() -> bool:
            return current_state.current_turn == Player.player1

        def on_random_click():
            nonlocal last_clicked_index
            last_clicked_index = -1

        def on_normal_move(clicked_index: int):
            move = Move(
                move_type=MoveType.normal_move,
                start=last_clicked_index,
                end=clicked_index,
            )
            save_state(server.local_move(move=move))
            on_random_click()

        def on_leave_bar(clicked_index: int):
            move = Move(
                move_type=MoveType.leave_bar,
                start=backgammon.get_start_position(),
                end=clicked_index,
            )
            save_state(server.local_move(move=move))
            on_random_click()

        def on_bear_off(clicked_index: int):
            move = Move(
                move_type=MoveType.bear_off,
                start=clicked_index,
                end=24,
            )
            save_state(server.local_move(move=move))
            on_random_click()

        def on_choose_piece(clicked_index: int):
            nonlocal last_clicked_index
            last_clicked_index = clicked_index

            nonlocal highlighted_indexes
            highlighted_indexes = backgammon.get_possible_tracks(start=clicked_index)
            

        server.start()

        while run:
            clock.tick(config.FRAMERATE)
            screen.fill("black")
            cursor = pygame.SYSTEM_CURSOR_ARROW
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

            if last_clicked_index == -1 and is_my_turn() and not is_screen_on_top():
                highlighted_indexes = cls._get_highlighted_tracks(
                    graphics=graphics, backgammon=backgammon
                )

            graphics.highlight_tracks(highlighted_indexes)

            cursor = cls.get_cursor(
                graphics=graphics,
                buttons=game_buttons,
                backgammon=backgammon,
                condition=not is_screen_on_top() and is_my_turn(),
            )
            
            cursor = cls.get_cursor(
                graphics=graphics,
                buttons=always_on_buttons,
                backgammon=backgammon,
                condition=not is_screen_on_top(),
            )

            buttons_dict[GameScreenButtonKeys.DONE].toggle(
                disabled=not is_my_turn() or not backgammon.is_turn_done()
            )
            buttons_dict[GameScreenButtonKeys.UNDO].toggle(
                disabled=not backgammon.has_history() or not is_my_turn()
            )

            cls._check_buttons(
                screen=screen, buttons=all_buttons, condition=not is_screen_on_top()
            )

            for event in pygame.event.get():
                cls._check_quit(event=event, quit=quit)

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and not is_screen_on_top()
                ):
                    cls._click_buttons(buttons=always_on_buttons)

                    if is_my_turn():
                        cls._click_buttons(buttons=game_buttons)

                    cls._move_piece(
                        graphics=graphics,
                        backgammon=backgammon,
                        last_clicked_index=last_clicked_index,
                        on_random_click=on_random_click,
                        on_normal_move=on_normal_move,
                        on_leave_bar=on_leave_bar,
                        on_choose_piece=on_choose_piece,
                        on_bear_off=on_bear_off,
                    )
            
            if not GameManager.is_window_focused():
                UnfocusedMenu.start(screen=screen)       
            elif server.local_is_alone():
                close_options()
                WaitingMenu.start(screen=screen, leave=leave_button_click)
            elif options:
                OptionsMenu.start(screen=screen, close=close_options)
            else:
                pygame.mouse.set_cursor(cursor)

            pygame.display.flip()


class OnlineClientGame(GameScreen):
    
    @classmethod
    def start(cls, screen: Surface, clock: Clock, ip_address: str):
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
        current_state: OnlineGameState = Backgammon().get_state().to_online(
            online_color=ColorConverter.pygame_to_pydantic(piece_color),
            local_color=ColorConverter.pygame_to_pydantic(piece_color),
        )
        current_state.current_turn = Player.player2
        started = False

        network = Network(
            ip_address=ip_address,
            port=config.GAME_PORT,
            buffer_size=config.NETWORK_BUFFER,
            timeout=10,
        )

        def quit():
            leave_button_click()
            GameManager.quit()
        
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

        def is_screen_on_top():
            nonlocal options
            return options or not GameManager.is_window_focused() or is_reconnecting()
        
        highlighted_indexes = []

        buttons_dict = cls._get_buttons(
            on_leave=leave_button_click,
            on_done=done_button_click,
            on_options=open_options,
            on_undo=undo_button_click,
            graphics=graphics,
        )

        all_buttons = [buttons_dict[key] for key in buttons_dict]

        game_buttons = [
            buttons_dict[GameScreenButtonKeys.DONE],
            buttons_dict[GameScreenButtonKeys.UNDO],
        ]
        always_on_buttons = [
            buttons_dict[GameScreenButtonKeys.LEAVE],
            buttons_dict[GameScreenButtonKeys.OPTIONS],
        ]

        def is_my_turn() -> bool:
            return current_state.current_turn == Player.player1

        time = pygame.time.get_ticks()

        def on_random_click():
            nonlocal last_clicked_index
            last_clicked_index = -1

        def on_normal_move(clicked_index: int):
            move = Move(
                move_type=MoveType.normal_move,
                start=last_clicked_index,
                end=clicked_index,
            )
            network.send(data=move, callback=save_state)
            on_random_click()

        def on_leave_bar(clicked_index: int):
            move = Move(
                move_type=MoveType.leave_bar,
                start=backgammon.get_start_position(),
                end=clicked_index,
            )
            network.send(data=move, callback=save_state)
            on_random_click()

        def on_bear_off(clicked_index: int):
            move = Move(
                move_type=MoveType.bear_off, start=clicked_index, end=24
            )
            network.send(data=move, callback=save_state)
            on_random_click()

        def on_choose_piece(clicked_index: int):
            nonlocal last_clicked_index
            last_clicked_index = clicked_index

            nonlocal highlighted_indexes
            highlighted_indexes = backgammon.get_possible_tracks(start=clicked_index)
            
        
        while run:
            clock.tick(config.FRAMERATE)
            screen.fill("black")
            cursor = pygame.SYSTEM_CURSOR_ARROW

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
            if last_clicked_index == -1 and is_my_turn() and not is_screen_on_top() and started:
                highlighted_indexes = cls._get_highlighted_tracks(
                    graphics=graphics, backgammon=backgammon
                )

            graphics.highlight_tracks(highlighted_indexes)

            cursor = cls.get_cursor(
                graphics=graphics,
                buttons=game_buttons,
                backgammon=backgammon,
                condition=not is_screen_on_top() and is_my_turn(),
            )
            
            cursor = cls.get_cursor(
                graphics=graphics,
                buttons=always_on_buttons,
                backgammon=backgammon,
                condition=not is_screen_on_top(),
            )

            buttons_dict[GameScreenButtonKeys.DONE].toggle(
                disabled=not is_my_turn() or not backgammon.is_turn_done()
            )
            buttons_dict[GameScreenButtonKeys.UNDO].toggle(
                disabled=not backgammon.has_history() or not is_my_turn()
            )

            cls._check_buttons(
                screen=screen, buttons=all_buttons, condition=not is_screen_on_top()
            )

            for event in pygame.event.get():
                cls._check_quit(event=event, quit=quit)
                
                if event.type == pygame.MOUSEBUTTONDOWN and not is_screen_on_top():
                    cls._click_buttons(buttons=always_on_buttons)

                    if is_my_turn():
                        cls._click_buttons(buttons=game_buttons)

                    cls._move_piece(
                        graphics=graphics,
                        backgammon=backgammon,
                        last_clicked_index=last_clicked_index,
                        on_random_click=on_random_click,
                        on_normal_move=on_normal_move,
                        on_leave_bar=on_leave_bar,
                        on_choose_piece=on_choose_piece,
                        on_bear_off=on_bear_off,
                    )

            if not GameManager.is_window_focused():
                UnfocusedMenu.start(screen=screen)       
            elif is_reconnecting():
                ReconnectingMenu.start(screen=screen)
                if not network.connected:
                    run = False
            elif options:
                OptionsMenu.start(screen=screen, close=close_options)
            else:
                pygame.mouse.set_cursor(cursor)

            pygame.display.flip()