import pygame
import pygame.gfxdraw
from config import FRAMERATE, BUTTON_COLOR, BUTTON_HOVER_COLOR, RESOLUTION
from graphics.graphics_manager import GraphicsManager, get_font
from backgammon.backgammon import Backgammon
from graphics.button import Button
from models.player import Player
import math

    
def offline_game(screen: pygame.Surface, clock: pygame.time.Clock):
    run = True
    player1_color = pygame.Color(100,100,100)
    player2_color = pygame.Color(150,100,100)
    graphics = GraphicsManager(screen=screen, player1_color=player1_color, player2_color=player2_color)
    backgammon = Backgammon()
    clicked_index = -1
    
    
    highlighted_indexes = backgammon.get_movable_counters()
    
    buttons_center = math.floor(RESOLUTION[1] + (RESOLUTION[0] - RESOLUTION[1]) / 4 * 3)
    DONE_BUTTON = Button(None, position=(buttons_center, 300), text_input="DONE",font=get_font(50),
                            base_color=BUTTON_COLOR, hovering_color=BUTTON_HOVER_COLOR, on_click=backgammon.switch_turn)
    UNDO_BUTTON = Button(None, position=(buttons_center, 420), text_input="UNDO",font=get_font(50),
                            base_color=BUTTON_COLOR, hovering_color=BUTTON_HOVER_COLOR, on_click=backgammon.undo)
    DONE_BUTTON.toggle()
    UNDO_BUTTON.toggle()
        
      
    game_buttons = [DONE_BUTTON, UNDO_BUTTON]
    
    
    
    while run:
        clock.tick(FRAMERATE)
        screen.fill("black")
        cursor = pygame.SYSTEM_CURSOR_ARROW
        MOUSE_POSITION = pygame.mouse.get_pos()
        
        GraphicsManager.render_background(screen=screen)

        DICE_TEXT = get_font(70).render(str(backgammon.dice['die1']) + " " + str(backgammon.dice['die2']), True, "white")
        DICE_TEXT_RECT = DICE_TEXT.get_rect(center=(buttons_center, 560))
        screen.blit(DICE_TEXT, DICE_TEXT_RECT)
        
        if clicked_index == -1:
            if backgammon.get_captured_pieces() > 0:
                highlighted_indexes = backgammon.get_bar_leaving_positions()
            else:
                highlighted_indexes = backgammon.get_movable_counters()
            
                
        graphics.render_board(backgammon.board, backgammon.bar, backgammon.home)
        
        graphics.highlight_tracks(highlighted_indexes)
        if graphics.check_tracks_input(mouse_position=MOUSE_POSITION) or \
            graphics.check_home_track_input(mouse_position=MOUSE_POSITION, player=backgammon.current_turn):
            cursor = pygame.SYSTEM_CURSOR_HAND
        
        DONE_BUTTON.toggle(disabled=not backgammon.is_turn_done())    
        UNDO_BUTTON.toggle(disabled=not backgammon.has_history())

        
        for button in game_buttons:
            button.check_hover(MOUSE_POSITION)
            button.update(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                if DONE_BUTTON.check_for_input(MOUSE_POSITION):
                    DONE_BUTTON.click()
                    DONE_BUTTON.toggle()
                    if backgammon.is_game_over():
                        print(backgammon.get_winner())
                        run = False
                
                if UNDO_BUTTON.check_for_input(MOUSE_POSITION):
                    UNDO_BUTTON.click()
                    highlighted_indexes = backgammon.get_movable_counters()    
                
                did_hit_target = False
                if graphics.check_home_track_input(mouse_position=MOUSE_POSITION, player=backgammon.current_turn):
                    backgammon.bear_off(position=clicked_index)
                        
                for index in range(24):
                    if graphics.check_track_input(mouse_position=MOUSE_POSITION, index=index):
                        did_hit_target = True
                        
                        if(clicked_index == -1 and backgammon.get_captured_pieces() == 0):
                            clicked_index = index
                            highlighted_indexes = backgammon.get_possible_tracks(clicked_index)
                            print(highlighted_indexes)
                        else:
                            if backgammon.get_captured_pieces() > 0:
                                backgammon.leave_bar(dice_value=abs(backgammon.get_start_position() - index))  
                            else: 
                                backgammon.make_move(start=clicked_index, end=index)
                                
                            # a piece had been moved
                            highlighted_indexes = backgammon.get_movable_counters()
                            clicked_index = -1
                
                clicked_index = -1 if not did_hit_target else clicked_index
                print(clicked_index)
                        
            
        pygame.mouse.set_cursor(cursor)
        pygame.display.update()