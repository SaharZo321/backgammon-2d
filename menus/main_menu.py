from graphics.text_button import TextButton
from graphics.button import Button
from config import FRAMERATE, BUTTON_COLOR, BUTTON_HOVER_COLOR
from graphics.graphics_manager import get_font, get_mid_width
from menus.play_menu import play_menu
from menus.options import options_menu
import pygame
from game_manager import GameManager
from graphics.graphics_manager import GraphicsManager
from graphics.outline_text import OutlineText



def main_menu(screen: pygame.Surface, clock: pygame.time.Clock) -> None:
    run = True
    
    def play_button_click():
        play_menu(screen, clock)
    
    def options_button_click():
        options_menu(screen, clock)
        
    def quit_button_click():
        GameManager.quit()
    
    MENU_TEXT = OutlineText.render(text="MAIN MANU",font=get_font(100), gfcolor=pygame.Color("white"), ocolor=pygame.Color("black"))
    MENU_RECT = MENU_TEXT.get_rect(center=(get_mid_width(), 100))

    PLAY_BUTTON = Button(
        position=(get_mid_width(), 300),
        text_input="PLAY",
        font=get_font(75),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        on_click=play_button_click
    )
    
    OPTIONS_BUTTON = TextButton(
        background_image=None,
        position=(get_mid_width(), 450),
        text_input="OPTIONS",
        font=get_font(75),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        on_click=options_button_click
    )
    
    QUIT_BUTTON = TextButton(
        background_image=None,
        position=(get_mid_width(), 650),
        text_input="QUIT",
        font=get_font(50),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        on_click=quit_button_click
    )
    
    buttons: list[TextButton] = [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]
    while run:
        clock.tick(FRAMERATE)

        screen.fill("black")
        
        GraphicsManager.render_background(screen=screen)
        
        MENU_MOUSE_POSITION = pygame.mouse.get_pos()
        
        screen.blit(MENU_TEXT, MENU_RECT)
        

        for button in buttons:
            button.change_color(MENU_MOUSE_POSITION)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameManager.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if(button.check_for_input(MENU_MOUSE_POSITION)):
                        button.click()

        pygame.display.update()