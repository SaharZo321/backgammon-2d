import pygame
from graphics.button import Button
from graphics.graphics_manager import get_font, get_mid_width
from menus.offline_game import offline_game
from config import FRAMERATE, BUTTON_COLOR, BUTTON_HOVER_COLOR
from game_manager import GameManager
from graphics.graphics_manager import GraphicsManager




def play_menu(screen: pygame.Surface, clock: pygame.time.Clock) -> None:
    run = True
    
    def back():
        nonlocal run
        run = False
        
    def goto_offline_game():
        offline_game(screen, clock)

    MENU_TEXT = get_font(70).render("How do you want to play?", True, "white")
    MENU_RECT = MENU_TEXT.get_rect(center=(get_mid_width(), 100))

    ONLINE_BUTTON = Button(None, position=(get_mid_width(), 300), text_input="PLAY ONLINE",font=get_font(75),
                            base_color=BUTTON_COLOR, hovering_color=BUTTON_HOVER_COLOR)
    OFFLINE_BUTTON = Button(None, position=(get_mid_width(), 450), text_input="PLAY OFFLINE",font=get_font(75),
                            base_color=BUTTON_COLOR, hovering_color=BUTTON_HOVER_COLOR, on_click=goto_offline_game)
    BACK_BUTTON = Button(None, position=(get_mid_width(), 650), text_input="BACK",font=get_font(50),
                            base_color=BUTTON_COLOR, hovering_color=BUTTON_HOVER_COLOR, on_click=back)
    buttons: list[Button] = [ONLINE_BUTTON, OFFLINE_BUTTON, BACK_BUTTON]
    while run:
        screen.fill("black")
        GraphicsManager.render_background(screen=screen)
        
        clock.tick(FRAMERATE)
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