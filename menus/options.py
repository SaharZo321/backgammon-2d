import pygame
from typing import Callable
from graphics.text_button import TextButton
from graphics.graphics_manager import get_font, get_mid_width
from config import FRAMERATE, BUTTON_COLOR, BUTTON_HOVER_COLOR, RESOLUTION
from game_manager import GameManager
from graphics.graphics_manager import GraphicsManager


def options_menu(
    screen: pygame.Surface, close: Callable[[], None]
) -> None:

    menu_surface = pygame.Surface(size=RESOLUTION, flags=pygame.SRCALPHA, depth=32)
    menu_surface.convert_alpha()
    menu_surface.fill(pygame.Color(0, 0, 0, 200))
    screen.blit(source=menu_surface, dest=(0, 0))

    def visuals_button_click():
        pass

    VISUALS_BUTTON = TextButton(
        background_image=None,
        position=(get_mid_width(), 270),
        text_input="EXAMPLE",
        font=get_font(75),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        outline_color=pygame.Color("black"),
        on_click=visuals_button_click,
    )

    BACK_BUTTON = TextButton(
        background_image=None,
        position=(get_mid_width(), 650),
        text_input="BACK",
        font=get_font(50),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        outline_color=pygame.Color("black"),
        outline_size=1,
        on_click=close,
    )

    buttons: list[TextButton] = [VISUALS_BUTTON, BACK_BUTTON]

    MOUSE_POSITION = pygame.mouse.get_pos()

    for button in buttons:
        button.change_color(MOUSE_POSITION)
        button.update(screen)

    if any(button.check_for_input(MOUSE_POSITION) for button in buttons):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            GameManager.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if button.check_for_input(MOUSE_POSITION):
                    button.click()
