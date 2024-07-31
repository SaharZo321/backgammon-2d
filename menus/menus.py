import math
from typing import Callable

from pygame.time import Clock
import config
from config import get_font
from decorators import debounce, throttle
from game_manager import GameManager
from graphics.elements import BetterButtonElement, Element
from graphics.graphics_manager import GraphicsManager, draw_border, gradient_surface
from graphics.outline_text import OutlineText
from graphics.elements import ButtonElement, SliderElement
from graphics.styled_elements import StyledBetterButton, StyledButton, StyledSlider
from menus.screen import Screen
import pygame

from models import ColorConverter, Position


class Menu(Screen):
    """Rendered on top of another screen. Uses its events"""
    @classmethod
    def start(
        cls,
        screen: pygame.Surface,
        close: Callable[[], None],
        events: list[pygame.event.Event],
    ):
        pass
        raise NotImplementedError()


class OptionsMenu(Menu):
    
    current_color = ColorConverter.pydantic_to_pygame(GameManager.options.piece_color)
    current_volume = GameManager.options.volume
    

    red_slider = StyledSlider(
        min_value=0,
        max_value=255,
        label="RED",
        position=Position(coords=(config.SCREEN.centerx, 190)),
        label_color=pygame.Color("red"),
        default_value=current_color.r,
        label_position="top",
        id="red",
        slider_surface=draw_border(
            surface=gradient_surface(
                left_colour=pygame.Color("black"),
                right_colour=pygame.Color("red"),
                size=(150, 30),
            ),
            width=2,
            color=pygame.Color("black"),
        ),
    )

    green_slider = StyledSlider(
        min_value=0,
        max_value=255,
        label="GREEN",
        position=Position(coords=(config.SCREEN.centerx, 270)),
        default_value=current_color.g,
        id="green",
        label_position="top",
        label_color=pygame.Color("green"),
        slider_surface=draw_border(
            surface=gradient_surface(
                left_colour=pygame.Color("black"),
                right_colour=pygame.Color("green"),
                size=(150, 30),
            ),
            width=2,
            color=pygame.Color("black"),
        ),
    )

    blue_slider = StyledSlider(
        min_value=0,
        max_value=255,
        label="BLUE",
        position=Position(coords=(config.SCREEN.centerx, 350)),
        default_value=current_color.b,
        id="blue",
        label_color=pygame.Color("blue"),
        label_position="top",
        slider_surface=draw_border(
            surface=gradient_surface(
                left_colour=pygame.Color("black"),
                right_colour=pygame.Color("blue"),
                size=(150, 30),
            ),
            width=2,
            color=pygame.Color("black"),
        ),
    )

    volume_button = StyledBetterButton(
        position=Position(coords=(50, 50)),
        image=pygame.transform.scale(
            config.MUTE_ICON if current_volume == 0 else config.VOLUME_ICON,
            (30, 30),
        ),
        padding=15,
    )
    
    volume_slider = StyledSlider(
        min_value=0,
        max_value=1,
        step=0.05,
        label=volume_button,
        position=Position(coords=(config.SCREEN.centerx, 470)),
        default_value=current_volume,
        label_position="top",
        id="volume",
    )

    back_button = StyledButton(
        position=Position(coords=(config.SCREEN.centerx, 650)),
        text_input="BACK",
        font=get_font(50),
    )
    
    options_text = OutlineText(
        text="OPTIONS",
        font=get_font(80),
        text_color=pygame.Color("white"),
        outline_color=pygame.Color("black"),
        outline_width=3,
        position=Position(coords=(config.SCREEN.centerx, 70)),
    )
    
    elements: list[Element] = [
        back_button,
        volume_button,
        green_slider,
        red_slider,
        blue_slider,
        volume_slider,
    ]
    
    @classmethod
    def get_volume_button_image(cls):
        return pygame.transform.scale(
            config.MUTE_ICON if cls.current_volume == 0 else config.VOLUME_ICON,
            (30, 30),
        )
    
    @classmethod
    def set_volume(cls, value: float, id: str | None = None):
        GameManager.set_volume(value)

    @classmethod
    @debounce(0.1)
    def set_color(cls, value: float, id: str):
        color = {
            "red": cls.current_color.r,
            "green": cls.current_color.g,
            "blue": cls.current_color.b,
        }
        color[id] = math.floor(value)
        new_color = ColorConverter.pygame_to_pydantic(pygame.Color(color["red"], color["green"], color["blue"]))
        GameManager.options.piece_color = new_color
    
    @classmethod
    def toggle_mute(cls):
        if cls.current_volume > 0:
            GameManager.options.mute_volume = GameManager.options.volume
            cls.volume_slider.value = 0
        else:
            cls.volume_slider.value = GameManager.options.mute_volume
        
    
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

        cls.current_color = ColorConverter.pydantic_to_pygame(GameManager.options.piece_color)
        cls.current_volume = GameManager.options.volume

        cls.back_button.on_click = close
        cls.blue_slider.on_value_change = cls.set_color
        cls.green_slider.on_value_change = cls.set_color
        cls.red_slider.on_value_change = cls.set_color
        cls.volume_slider.on_value_change = cls.set_volume
        cls.volume_button.on_click = cls.toggle_mute
        cls.volume_button.image = cls.get_volume_button_image()
        
        GraphicsManager.render_piece(
            screen, center=(450, 290), color=cls.current_color, radius=50
        )
        
        cls.options_text.update(screen)
        
        pygame.mouse.set_cursor(cls._get_cursor(elements=cls.elements))
        cls.render_elements(screen=screen, elements=cls.elements, events=events)
        cls.click_elements(elements=cls.elements, events=events)


class ConnectingMenu(Menu):

    @classmethod
    def start(cls, screen: pygame.Surface) -> None:
        menu_surface = pygame.Surface(
            size=config.RESOLUTION, flags=pygame.SRCALPHA, depth=32
        )
        menu_surface.convert_alpha()
        menu_surface.fill(pygame.Color(0, 0, 0, 180))
        screen.blit(source=menu_surface, dest=(0, 0))

        OutlineText.render(
            text="CONNECTING...",
            font=get_font(100),
            text_color=pygame.Color("white"),
            outline_color=pygame.Color("black"),
            outline_width=3,
            surface=screen,
            position=Position(coords=(config.SCREEN.centerx, 300)),
        )

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


class UnfocusedMenu(Menu):

    @classmethod
    def start(cls, screen: pygame.Surface) -> None:
        menu_surface = pygame.Surface(
            size=config.RESOLUTION, flags=pygame.SRCALPHA, depth=32
        )
        menu_surface.convert_alpha()
        menu_surface.fill(pygame.Color(0, 0, 0, 180))
        screen.blit(source=menu_surface, dest=(0, 0))

        OutlineText.render(
            surface=screen,
            text="UNFOCUSED...",
            font=get_font(100),
            text_color=pygame.Color("white"),
            outline_color=pygame.Color("black"),
            outline_width=3,
            position=Position(coords=(config.SCREEN.centerx, round(config.RESOLUTION[1] / 2.5))),
        )

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


class WaitingMenu(Menu):

    @classmethod
    def start(
        cls,
        screen: pygame.Surface,
        close: Callable[[], None],
        events: list[pygame.event.Event],
    ):
        menu_surface = pygame.Surface(
            size=config.RESOLUTION, flags=pygame.SRCALPHA, depth=32
        )
        menu_surface.convert_alpha()
        menu_surface.fill(pygame.Color(0, 0, 0, 180))
        screen.blit(source=menu_surface, dest=(0, 0))

        OutlineText.render(
            text="PLAYER 2 NOT CONNECTED",
            font=get_font(60),
            text_color=pygame.Color("white"),
            outline_color=pygame.Color("black"),
            outline_width=3,
            position=Position(coords=(config.SCREEN.centerx, 200)),
            surface=screen,
        )

        OutlineText.render(
            text="WATING",
            font=get_font(80),
            text_color=pygame.Color("white"),
            outline_color=pygame.Color("black"),
            outline_width=3,
            position=Position(coords=(config.SCREEN.centerx, 400)),
            surface=screen,
        )

        leave_button = BetterButtonElement(
            position=Position(coords=(config.SCREEN.centerx, 650)),
            text_input="LEAVE",
            font=get_font(50),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            on_click=close,
        )

        cls.render_elements(screen=screen, elements=[leave_button], events=events)
        pygame.mouse.set_cursor(cls._get_cursor(elements=[leave_button]))

        cls.click_elements(elements=[leave_button], events=events)


class LostConnectionMenu(Menu):

    @classmethod
    def start(
        cls,
        screen: pygame.Surface,
        close: Callable[[], None],
        events: list[pygame.event.Event],
    ):
        menu_surface = pygame.Surface(
            size=config.RESOLUTION, flags=pygame.SRCALPHA, depth=32
        )
        menu_surface.convert_alpha()
        menu_surface.fill(pygame.Color(0, 0, 0, 180))
        screen.blit(source=menu_surface, dest=(0, 0))

        OutlineText.render(
            text="LOST CONNECTION",
            font=get_font(80),
            text_color=pygame.Color("white"),
            outline_color=pygame.Color("black"),
            outline_width=3,
            position=Position(coords=(config.SCREEN.centerx, 300)),
            surface=screen,
        )

        OutlineText.render(
            text="TO THE SERVER",
            font=get_font(80),
            text_color=pygame.Color("white"),
            outline_color=pygame.Color("black"),
            outline_width=3,
            position=Position(coords=(config.SCREEN.centerx, 400)),
            surface=screen,
        )

        leave_button = BetterButtonElement(
            position=Position(coords=(config.SCREEN.centerx, 650)),
            text_input="LEAVE",
            font=get_font(50),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            on_click=close,
        )

        cls.render_elements(screen=screen, elements=[leave_button], events=events)
        pygame.mouse.set_cursor(cls._get_cursor(elements=[leave_button]))

        cls.click_elements(elements=[leave_button], events=events)
        
