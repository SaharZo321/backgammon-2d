from graphics.button import Button
from config import FRAMERATE, BUTTON_COLOR, BUTTON_HOVER_COLOR
from graphics.graphics_manager import get_font, get_mid_width
from menus.play_menu import play_menu
import pygame
from game_manager import GameManager
from graphics.graphics_manager import GraphicsManager
from graphics.outline_text import OutlineText



def main_menu(screen: pygame.Surface, clock: pygame.time.Clock) -> None:
    run = True
    
    def goto_play_menu():
        play_menu(screen, clock)
        

    MENU_TEXT = OutlineText.render(text="MAIN MANU",font=get_font(100))
    MENU_RECT = MENU_TEXT.get_rect(center=(get_mid_width(), 100))

    PLAY_BUTTON = Button(None, position=(get_mid_width(), 300), text_input="PLAY",font=get_font(75),
                            base_color=BUTTON_COLOR, hovering_color=BUTTON_HOVER_COLOR,outline_color=pygame.Color("black"), outline_size=3, on_click=goto_play_menu)
    OPTIONS_BUTTON = Button(None, position=(get_mid_width(), 450), text_input="OPTIONS",font=get_font(75),
                            base_color=BUTTON_COLOR, hovering_color=BUTTON_HOVER_COLOR)
    QUIT_BUTTON = Button(None, position=(get_mid_width(), 650), text_input="QUIT",font=get_font(50),
                            base_color=BUTTON_COLOR, hovering_color=BUTTON_HOVER_COLOR, on_click=GameManager.quit)
    buttons: list[Button] = [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]
    while run:
        clock.tick(FRAMERATE)

        screen.fill("black")
        
        GraphicsManager.render_background(screen=screen)
        
        MENU_MOUSE_POSITION = pygame.mouse.get_pos()
        
        screen.blit(MENU_TEXT, MENU_RECT)
        

        for button in buttons:
            button.check_hover(MENU_MOUSE_POSITION)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameManager.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if(button.check_for_input(MENU_MOUSE_POSITION)):
                        button.click()

        pygame.display.update()