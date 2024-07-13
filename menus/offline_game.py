import pygame
import pygame.gfxdraw
from config import FRAMERATE, BUTTON_COLOR, BUTTON_HOVER_COLOR, RESOLUTION
from graphics.graphics_manager import GraphicsManager, get_font
from backgammon.backgammon import Backgammon
from graphics.button import Button
from graphics.outline_text import OutlineText
import math


def offline_game(screen: pygame.Surface, clock: pygame.time.Clock):
    run = True
    player1_color = pygame.Color(100, 100, 100)
    player2_color = pygame.Color(150, 100, 100)
    graphics = GraphicsManager(
        screen=screen, player1_color=player1_color, player2_color=player2_color
    )
    backgammon = Backgammon()
    clicked_index = -1

    def leave_button_click():
        nonlocal run
        run = False

    def done_button_click():
        backgammon.switch_turn()
        DONE_BUTTON.toggle()
        if backgammon.is_game_over():
            print(backgammon.get_winner())
            nonlocal run
            run = False

    def undo_button_click():
        backgammon.undo()
        nonlocal highlighted_indexes
        highlighted_indexes = backgammon.get_movable_counters()

    highlighted_indexes = backgammon.get_movable_counters()

    buttons_center = math.floor((GraphicsManager.RECT.right + screen.get_width()) / 2)

    DONE_BUTTON = Button(
        background_image=None,
        position=(buttons_center, 300),
        text_input="DONE",
        font=get_font(50),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        on_click=done_button_click,
    )

    UNDO_BUTTON = Button(
        background_image=None,
        position=(buttons_center, 420),
        text_input="UNDO",
        font=get_font(50),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        on_click=undo_button_click,
    )

    LEAVE_BUTTON = Button(
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

    DONE_BUTTON.toggle()
    UNDO_BUTTON.toggle()

    game_buttons = [DONE_BUTTON, UNDO_BUTTON, LEAVE_BUTTON]

    while run:
        clock.tick(FRAMERATE)
        screen.fill("black")
        cursor = pygame.SYSTEM_CURSOR_ARROW
        MOUSE_POSITION = pygame.mouse.get_pos()

        GraphicsManager.render_background(screen=screen)
        dice_string = str(backgammon.dice["die1"]) + " " + str(backgammon.dice["die2"])

        DICE_TEXT = OutlineText.render(
            text=dice_string,
            font=get_font(70),
            gfcolor=pygame.Color("white"),
            ocolor=pygame.Color("black"),
        )

        DICE_TEXT_RECT = DICE_TEXT.get_rect(center=(buttons_center, 560))
        screen.blit(DICE_TEXT, DICE_TEXT_RECT)

        if clicked_index == -1:
            if backgammon.get_captured_pieces() > 0:
                highlighted_indexes = backgammon.get_bar_leaving_positions()
            else:
                highlighted_indexes = backgammon.get_movable_counters()

        graphics.render_board(backgammon.board, backgammon.bar, backgammon.home)

        graphics.highlight_tracks(highlighted_indexes)
        if graphics.check_tracks_input(
            mouse_position=MOUSE_POSITION
        ) or graphics.check_home_track_input(
            mouse_position=MOUSE_POSITION, player=backgammon.current_turn
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
            if event.type == pygame.MOUSEBUTTONDOWN:

                for button in game_buttons:
                    if button.check_for_input(mouse_position=MOUSE_POSITION):
                        button.click()

                did_hit_target = False
                if graphics.check_home_track_input(
                    mouse_position=MOUSE_POSITION, player=backgammon.current_turn
                ):
                    backgammon.bear_off(position=clicked_index)

                for index in range(24):
                    if graphics.check_track_input(
                        mouse_position=MOUSE_POSITION, index=index
                    ):
                        did_hit_target = True

                        if (
                            clicked_index == -1
                            and backgammon.get_captured_pieces() == 0
                        ):
                            clicked_index = index
                            highlighted_indexes = backgammon.get_possible_tracks(
                                clicked_index
                            )
                            print(highlighted_indexes)

                        else:
                            if backgammon.get_captured_pieces() > 0:
                                backgammon.leave_bar(
                                    dice_value=abs(
                                        backgammon.get_start_position() - index
                                    )
                                )

                            else:
                                backgammon.make_move(start=clicked_index, end=index)

                            # a piece had been moved
                            highlighted_indexes = backgammon.get_movable_counters()
                            clicked_index = -1

                clicked_index = -1 if not did_hit_target else clicked_index
                print(clicked_index)

        pygame.mouse.set_cursor(cursor)
        pygame.display.update()
