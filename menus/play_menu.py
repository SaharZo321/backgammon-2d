import pygame
from graphics.button import Button
from graphics.graphics_manager import get_font, get_mid_width
from menus.offline_game import offline_game
from config import FRAMERATE, BUTTON_COLOR, BUTTON_HOVER_COLOR
from game_manager import GameManager
from graphics.graphics_manager import GraphicsManager


def play_menu(screen: pygame.Surface, clock: pygame.time.Clock) -> None:
    run = True

    def back_button_click():
        nonlocal run
        run = False

    def offline_button_click():
        offline_game(screen, clock)

    def online_button_click():
        pass

    ONLINE_BUTTON = Button(
        background_image=None,
        position=(get_mid_width(), 270),
        text_input="PLAY ONLINE",
        font=get_font(75),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        outline_color=pygame.Color("black"),
        outline_size=1,
        on_click=online_button_click,
    )

    OFFLINE_BUTTON = Button(
        background_image=None,
        position=(get_mid_width(), 420),
        text_input="PLAY OFFLINE",
        font=get_font(75),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        outline_color=pygame.Color("black"),
        outline_size=1,
        on_click=offline_button_click,
    )

    BACK_BUTTON = Button(
        background_image=None,
        position=(get_mid_width(), 650),
        text_input="BACK",
        font=get_font(50),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        outline_color=pygame.Color("black"),
        outline_size=1,
        on_click=back_button_click,
    )

    buttons: list[Button] = [ONLINE_BUTTON, OFFLINE_BUTTON, BACK_BUTTON]

    while run:
        screen.fill("black")
        GraphicsManager.render_background(screen=screen)

        clock.tick(FRAMERATE)
        MENU_MOUSE_POSITION = pygame.mouse.get_pos()

        for button in buttons:
            button.change_color(MENU_MOUSE_POSITION)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameManager.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.check_for_input(MENU_MOUSE_POSITION):
                        button.click()

        pygame.display.update()
