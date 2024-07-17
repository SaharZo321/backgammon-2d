import pygame
import math
import ipaddress
from graphics.text_button import TextButton
from graphics.button import Button
from graphics.graphics_manager import get_font, get_mid_width
from config import FRAMERATE, BUTTON_COLOR, BUTTON_HOVER_COLOR, RESOLUTION
from game_manager import GameManager, SettingsKeys
from graphics.graphics_manager import GraphicsManager
from graphics.outline_text import OutlineText
from menus.games.online_client import online_client


def _is_valid_ip(address: str):
    try:
        return ipaddress.IPv4Address(address).is_private
    except:
        return False

def _render_menu(
    screen: pygame.Surface,
    buttons: list[TextButton],
    mouse_position: tuple[int, int],
):
    screen.fill("black")

    GraphicsManager.render_background(screen)
    
    MENU_TEXT = OutlineText.render(
        text="Enter IP Address",
        font=get_font(70),
        gfcolor=pygame.Color("white"),
        ocolor=pygame.Color("black"),
    )
    MENU_RECT = MENU_TEXT.get_rect(center=(get_mid_width(), 80))
    screen.blit(MENU_TEXT, MENU_RECT)


    for button in buttons:
        button.change_color(mouse_position)
        button.update(screen)

    if any(button.check_for_input(mouse_position=mouse_position) for button in buttons):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


def ip_menu(screen: pygame.Surface, clock: pygame.time.Clock) -> None:

    run = True

    active = False
    
    colors = {
        False: pygame.Color("gray"),
        True: pygame.Color("white")
    }
    
    ip_address = GameManager.get_setting(SettingsKeys.IP)

    MIN_STR = "M"

    def back_click():
        nonlocal run
        run = False

    def join_click():
        online_client(screen=screen, clock=clock, ip_address=ip_address)
        GameManager.set_setting(SettingsKeys.IP, ip_address)
        back_click()

    JOIN_BUTTON = Button(
        position=(math.floor(get_mid_width()), 500),
        text_input="JOIN",
        font=get_font(70),
        text_color=pygame.Color("black"),
        base_color=BUTTON_COLOR,
        hovering_color=BUTTON_HOVER_COLOR,
        outline_color=pygame.Color("black"),
        on_click=join_click,
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
        on_click=back_click,
    )

    buttons: list[TextButton] = [BACK_BUTTON, JOIN_BUTTON]

    while run:

        clock.tick(FRAMERATE)
        MOUSE_POSITION = pygame.mouse.get_pos()
        
        JOIN_BUTTON.toggle(disabled=not _is_valid_ip(ip_address))
        
        _render_menu(screen=screen, buttons=buttons, mouse_position=MOUSE_POSITION)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameManager.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.check_for_input(MOUSE_POSITION):
                        button.click()

                if FIELD_BACKGROUND_RECT.collidepoint(MOUSE_POSITION):
                    active = True
                else:
                    active = False

            if event.type == pygame.KEYDOWN and active:
                # Check for backspace
                if event.key == pygame.K_BACKSPACE:

                    # get text input from 0 to -1 i.e. end.
                    ip_address = ip_address[:-1]
                elif event.key == pygame.K_ESCAPE:
                    active = False
                # Unicode standard is used for string
                # formation
                else:
                    ip_address += event.unicode

        FIELD_TEXT = OutlineText.render(
            text=ip_address,
            font=get_font(80),
            gfcolor=pygame.Color("white"),
            ocolor=pygame.Color("black"),
        )
        FIELD_RECT = FIELD_TEXT.get_rect(center=(get_mid_width(), 320))

        MIN_FIELD_BACKGROUND_RECT = (
            get_font(80)
            .render(
                MIN_STR,
                True,
                pygame.Color("white"),
            )
            .get_rect(center=(get_mid_width(), 320))
        )

        FIELD_BACKGROUND_RECT = (
            MIN_FIELD_BACKGROUND_RECT if len(ip_address) <= len(MIN_STR) else FIELD_RECT
        )

        pygame.draw.rect(
            surface=screen,
            color=colors[active],
            rect=FIELD_BACKGROUND_RECT.scale_by(1.1, 1.1),
            border_radius=20,
        )

        screen.blit(FIELD_TEXT, FIELD_RECT)

        pygame.display.flip()

