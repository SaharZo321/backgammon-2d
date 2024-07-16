import pygame
import math
from graphics.text_button import TextButton
from graphics.button import Button
from graphics.graphics_manager import get_font, get_mid_width
import config
from game_manager import GameManager
from graphics.graphics_manager import GraphicsManager
from menus.online_menu.ip import ip_menu
from menus.games.local_client import local_client
from graphics.outline_text import OutlineText


def _render_menu(screen: pygame.Surface, buttons: list[TextButton], mouse_position: tuple[int, int]):
    screen.fill("black")
    
    GraphicsManager.render_background(screen)
    
    for button in buttons:
            button.change_color(mouse_position)
            button.update(screen)
    
    if any(button.check_for_input(mouse_position=mouse_position) for button in buttons):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        

def online_menu(screen: pygame.Surface, clock: pygame.time.Clock) -> None:
    
    run = True
    
    def back_click():
        nonlocal run
        run = False

    def join_room_click():
        ip_menu(screen=screen, clock=clock)
        back_click()

    def create_room_click():
        local_client(screen=screen, clock=clock)
        back_click()
    
    JOIN_ROOM_BUTTON = Button(
        position=(math.floor(get_mid_width()), 270),
        text_input="JOIN ROOM",
        font=get_font(70),
        text_color=pygame.Color("black"),
        base_color=config.BUTTON_COLOR,
        hovering_color=config.BUTTON_HOVER_COLOR,
        outline_color=pygame.Color("black"),
        on_click=join_room_click,
    )
    
    CREATE_ROOM_BUTTON = Button(
        position=(math.floor(get_mid_width()), 420),
        text_input="CREATE ROOM",
        font=get_font(70),
        text_color=pygame.Color("black"),
        base_color=config.BUTTON_COLOR,
        hovering_color=config.BUTTON_HOVER_COLOR,
        outline_color=pygame.Color("black"),
        on_click=create_room_click,
    )

    BACK_BUTTON = TextButton(
        background_image=None,
        position=(get_mid_width(), 650),
        text_input="BACK",
        font=get_font(50),
        base_color=config.BUTTON_COLOR,
        hovering_color=config.BUTTON_HOVER_COLOR,
        outline_color=pygame.Color("black"),
        outline_size=1,
        on_click=back_click,
    )

    buttons: list[TextButton] = [JOIN_ROOM_BUTTON, BACK_BUTTON, CREATE_ROOM_BUTTON]

    while run:

        clock.tick(config.FRAMERATE)
        MOUSE_POSITION = pygame.mouse.get_pos()

        _render_menu(screen=screen, buttons=buttons, mouse_position=MOUSE_POSITION)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameManager.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.check_for_input(MOUSE_POSITION):
                        button.click()

        pygame.display.flip()
        
