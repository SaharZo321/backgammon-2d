import math
from typing import Callable
import config
from game_manager import GameManager
from graphics.buttons import BetterButton, Button
from graphics.graphics_manager import get_font, get_mid_width
from graphics.outline_text import OutlineText
from menus.screen import Screen
import pygame


class OptionsMenu(Screen):
    @classmethod
    def start(cls, screen: pygame.Surface, close: Callable[[], None], on_top = True) -> None:
        if on_top:
            menu_surface = pygame.Surface(
                size=config.RESOLUTION, flags=pygame.SRCALPHA, depth=32
            )
            menu_surface.convert_alpha()
            menu_surface.fill(pygame.Color(0, 0, 0, 200))
            screen.blit(source=menu_surface, dest=(0, 0))

        def visuals_button_click():
            pass

        VISUALS_BUTTON = Button(
            background_image=None,
            position=(get_mid_width(), 270),
            text_input="EXAMPLE",
            font=get_font(75),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            outline_color=pygame.Color("black"),
            on_click=visuals_button_click,
        )

        BACK_BUTTON = Button(
            background_image=None,
            position=(get_mid_width(), 650),
            text_input="BACK",
            font=get_font(50),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            outline_color=pygame.Color("black"),
            outline_size=1,
            on_click=close,
        )

        buttons: list[Button] = [VISUALS_BUTTON, BACK_BUTTON]

        pygame.mouse.set_cursor(cls._check_buttons(screen=screen, buttons=buttons))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameManager.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                cls._click_buttons(buttons=buttons)


class ReconnectingMenu(Screen):

    @classmethod
    def start(cls, screen: pygame.Surface) -> None:
        menu_surface = pygame.Surface(
            size=config.RESOLUTION, flags=pygame.SRCALPHA, depth=32
        )
        menu_surface.convert_alpha()
        menu_surface.fill(pygame.Color(0, 0, 0, 180))
        screen.blit(source=menu_surface, dest=(0, 0))

        CONNECTING = OutlineText.render(
            text="RECONNECTING...",
            font=get_font(100),
            gfcolor=pygame.Color("white"),
            ocolor=pygame.Color("black"),
            opx=3,
        )

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        CONNECTING_TEXT_RECT = CONNECTING.get_rect(center=(get_mid_width(), 300))

        screen.blit(CONNECTING, CONNECTING_TEXT_RECT)


class UnfocusedMenu(Screen):

    @classmethod
    def start(cls, screen: pygame.Surface) -> None:
        menu_surface = pygame.Surface(
            size=config.RESOLUTION, flags=pygame.SRCALPHA, depth=32
        )
        menu_surface.convert_alpha()
        menu_surface.fill(pygame.Color(0, 0, 0, 180))
        screen.blit(source=menu_surface, dest=(0, 0))

        UNFOCUSED = OutlineText.render(
            text="UNFOCUSED...",
            font=get_font(100),
            gfcolor=pygame.Color("white"),
            ocolor=pygame.Color("black"),
            opx=3,
        )

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        UNFOCUSED_TEXT_RECT = UNFOCUSED.get_rect(
            center=(get_mid_width(), math.floor(config.RESOLUTION[1] / 2.5))
        )

        screen.blit(UNFOCUSED, UNFOCUSED_TEXT_RECT)


class WaitingMenu(Screen):
    
    @classmethod
    def start(cls, screen: pygame.Surface, leave: Callable[[], None]):
        menu_surface = pygame.Surface(
            size=config.RESOLUTION, flags=pygame.SRCALPHA, depth=32
        )
        menu_surface.convert_alpha()
        menu_surface.fill(pygame.Color(0, 0, 0, 180))
        screen.blit(source=menu_surface, dest=(0, 0))

        PLAYER2_TEXT = OutlineText.render(
            text="PLAYER 2 NOT CONNECTED",
            font=get_font(60),
            gfcolor=pygame.Color("white"),
            ocolor=pygame.Color("black"),
            opx=3,
        )

        PLAYER2_TEXT_RECT = PLAYER2_TEXT.get_rect(center=(get_mid_width(), 200))

        screen.blit(PLAYER2_TEXT, PLAYER2_TEXT_RECT)

        WATING_TEXT = OutlineText.render(
            text="WATING",
            font=get_font(80),
            gfcolor=pygame.Color("white"),
            ocolor=pygame.Color("black"),
            opx=3,
        )

        WATING_TEXT_RECT = WATING_TEXT.get_rect(center=(get_mid_width(), 400))

        screen.blit(WATING_TEXT, WATING_TEXT_RECT)

        LEAVE_BUTTON = BetterButton(
            position=(get_mid_width(), 650),
            text_input="LEAVE",
            font=get_font(50),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            on_click=leave,
        )

        cursor = cls._check_buttons(screen=screen, buttons=[LEAVE_BUTTON])
        pygame.mouse.set_cursor(cursor)
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                cls._click_buttons([LEAVE_BUTTON])