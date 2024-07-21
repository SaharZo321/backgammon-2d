import math
from typing import Callable

from pygame.time import Clock
import config
from config import get_font
from game_manager import GameManager, SettingsKeys
from graphics.elements import BetterButtonElement, Element
from config import get_mid_width
from graphics.outline_text import OutlineText
from graphics.elements import ButtonElement, SliderElement
from menus.screen import Screen
import pygame


class Menu(Screen):
    @classmethod
    def start(cls, screen: pygame.Surface, close: Callable[[], None], events: list[pygame.event.Event]):
        pass
        raise NotImplementedError()


class OptionsMenu(Menu):
    @classmethod
    def start(
        cls,
        screen: pygame.Surface,
        close: Callable[[], None],
        events: list[pygame.event.Event],
        on_top=True,
    ) -> None:
        if on_top:
            menu_surface = pygame.Surface(
                size=config.RESOLUTION, flags=pygame.SRCALPHA, depth=32
            )
            menu_surface.convert_alpha()
            menu_surface.fill(pygame.Color(0, 0, 0, 200))
            screen.blit(source=menu_surface, dest=(0, 0))

        def visuals_button_click():
            pass
        
        current_color: pygame.Color = GameManager.get_setting(key=SettingsKeys.piece_color)
        
        def set_color(value: int, id: str):
            color = {
                "red": current_color.r,
                "green": current_color.g,
                "blue": current_color.b,
            }
            color[id] = value
            new_color = pygame.Color(color["red"], color["green"], color["blue"])
            GameManager.set_setting(key=SettingsKeys.piece_color, value=new_color)
        
        red_slider = SliderElement(
            min_value=0,
            max_value=255,
            label="RED",
            rect=pygame.Rect(150, 50, 150, 30),
            default_value=current_color.r,
            on_value_changed=set_color,
            id="red"
        )
        
        green_slider = SliderElement(
            min_value=0,
            max_value=255,
            label="GREEN",
            rect=pygame.Rect(150, 100, 150, 30),
            default_value=current_color.g,
            on_value_changed=set_color,
            id="green"
        )
        
        blue_slider = SliderElement(
            min_value=0,
            max_value=255,
            label="BLUE",
            rect=pygame.Rect(150, 150, 150, 30),
            default_value=current_color.b,
            on_value_changed=set_color,
            id="blue"
        )

        VISUALS_BUTTON = ButtonElement(
            background_image=None,
            position=(get_mid_width(), 270),
            text_input="EXAMPLE",
            font=get_font(75),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            outline_color=pygame.Color("black"),
            on_click=visuals_button_click,
        )

        BACK_BUTTON = ButtonElement(
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

        elements: list[Element] = [VISUALS_BUTTON, BACK_BUTTON] + [green_slider, red_slider, blue_slider]

        pygame.mouse.set_cursor(cls._get_cursor(elements=elements))
        cls._render_elements(screen=screen, elements=elements)

        for event in events:
            cls._check_quit(event, GameManager.quit)
            if event.type == pygame.MOUSEBUTTONDOWN:
                cls._click_elements(elements=elements)


class ReconnectingMenu(Menu):

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


class UnfocusedMenu(Menu):

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


class WaitingMenu(Menu):

    @classmethod
    def start(cls, screen: pygame.Surface, close: Callable[[], None], events: list[pygame.event.Event]):
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

        leave_button = BetterButtonElement(
            position=(get_mid_width(), 650),
            text_input="LEAVE",
            font=get_font(50),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            on_click=close,
        )

        cls._render_elements(screen=screen, elements=[leave_button])
        pygame.mouse.set_cursor(cls._get_cursor(elements=[leave_button]))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                cls._click_elements([leave_button])
