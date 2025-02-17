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

from models import ColorConverter, Player, Position


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

    current_player = Player.player1
    current_color = ColorConverter.pydantic_to_pygame(GameManager.options.player_colors[current_player])
    
    @staticmethod
    def switch_player():
        OptionsMenu.current_player = Player.other(OptionsMenu.current_player)
        OptionsMenu.player_button.text_input = str(OptionsMenu.current_player)
        current_color = OptionsMenu.get_current_color()
        OptionsMenu.red_slider.value = current_color.r
        OptionsMenu.green_slider.value = current_color.g
        OptionsMenu.blue_slider.value = current_color.b

    player_button = StyledBetterButton(
        position=Position(coords=(config.SCREEN.centerx, 210)),
        font=get_font(24),
        text_input="player1",
        on_click=switch_player
    )
    
    @staticmethod
    @debounce(0.1)
    def set_color(value: float, id: str):
        old_color = ColorConverter.pydantic_to_pygame(
            GameManager.options.player_colors[OptionsMenu.current_player]
        )
        color = {
            "r": old_color.r,
            "g": old_color.g,
            "b": old_color.b,
        }
        color[id] = round(value)

        new_color = pygame.Color(*color.values())

        GameManager.options.player_colors[OptionsMenu.current_player] = (
            ColorConverter.pygame_to_pydantic(new_color)
        )
    
    red_slider = StyledSlider(
        min_value=0,
        max_value=255,
        position=Position(coords=(config.SCREEN.centerx, 250)),
        default_value=current_color.r,
        id="r",
        slider_surface=draw_border(
            surface=gradient_surface(
                left_colour=pygame.Color("black"),
                right_colour=pygame.Color("red"),
                size=(150, 30),
            ),
            width=2,
            color=pygame.Color("black"),
        ),
        on_value_change=set_color
    )

    green_slider = StyledSlider(
        min_value=0,
        max_value=255,
        position=Position(coords=(config.SCREEN.centerx, 290)),
        default_value=current_color.g,
        id="g",
        slider_surface=draw_border(
            surface=gradient_surface(
                left_colour=pygame.Color("black"),
                right_colour=pygame.Color("green"),
                size=(150, 30),
            ),
            width=2,
            color=pygame.Color("black"),
        ),
        on_value_change=set_color
    )

    blue_slider = StyledSlider(
        min_value=0,
        max_value=255,
        position=Position(coords=(config.SCREEN.centerx, 330)),
        default_value=current_color.b,
        id="b",
        slider_surface=draw_border(
            surface=gradient_surface(
                left_colour=pygame.Color("black"),
                right_colour=pygame.Color("blue"),
                size=(150, 30),
            ),
            width=2,
            color=pygame.Color("black"),
        ),
        on_value_change=set_color
    )
    
    @staticmethod
    def get_volume_button_image():
        return pygame.transform.scale(
            config.MUTE_ICON if GameManager.sound_manager.volume == 0 else config.VOLUME_ICON,
            (30, 30),
        )

    @staticmethod
    def toggle_mute():
        if GameManager.sound_manager.volume > 0:
            GameManager.sound_manager.mute()
        else:
            GameManager.sound_manager.unmute()
        
        OptionsMenu.volume_slider.value = GameManager.sound_manager.volume
    
    volume_button = StyledBetterButton(
        position=Position(coords=(50, 50)),
        image=get_volume_button_image(),
        padding=15,
        on_click=toggle_mute
    )
    
    @staticmethod
    def set_volume(value: float, id: str | None = None):
        GameManager.sound_manager.volume = value

    volume_slider = StyledSlider(
        min_value=0,
        max_value=1,
        step=0.05,
        label=volume_button,
        position=Position(coords=(config.SCREEN.centerx, 520)),
        default_value=GameManager.sound_manager.volume,
        label_position="top",
        id="volume",
        on_value_change=set_volume
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
        player_button,
    ]
    
    @classmethod
    def get_current_color(cls):
        return ColorConverter.pydantic_to_pygame(GameManager.options.player_colors[cls.current_player])

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

        cls.back_button.on_click = close
        cls.volume_button.image = cls.get_volume_button_image()
        cls.player_button.on_click = cls.switch_player

        GraphicsManager.render_piece(
            screen,
            center=(config.SCREEN.centerx, 400),
            color=cls.get_current_color(),
            radius=35,
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
            position=Position(
                coords=(config.SCREEN.centerx, round(config.RESOLUTION[1] / 2.5))
            ),
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
