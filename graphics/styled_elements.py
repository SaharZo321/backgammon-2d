from typing import Callable, Literal
from pygame import Color, Surface
import pygame
from pygame.font import Font
from pygame.mixer import Sound
import config
from game_manager import GameManager
from graphics.elements import (
    BetterButtonElement,
    ButtonElement,
    SliderElement,
    TextFieldElement,
)
from models import Position


class StyledBetterButton(BetterButtonElement):

    def __init__(
        self,
        position: Position = Position(),
        padding: int = 10,
        font: Font | None = None,
        text_input: str = "",
        image: Surface | None = None,
        on_click: Callable[[], None] = lambda: None,
    ) -> None:
        super().__init__(
            position=position,
            font=font,
            text_input=text_input,
            image=image,
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            on_click=on_click,
            sound=GameManager.get_sound("button"),
            padding=padding
        )


class StyledButton(ButtonElement):
    def __init__(
        self,
        font: Font | None = None,
        position: Position = Position(),
        text_input: str = "BUTTON",
        image: Surface | None = None,
        on_click: Callable[[], None] = lambda: None,
    ) -> None:
        super().__init__(
            font=font,
            position=position,
            text_input=text_input,
            image=image,
            on_click=on_click,
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            sound=GameManager.get_sound("button"),
        )


class StyledTextField(TextFieldElement):
    def __init__(
        self,
        font: Font,
        position: Position = Position(),
        width: int = 0,
        default: str = "",
        disabled: bool = True,
        text_align: Literal["right", "left", "center"] = "left",
        on_enter: Callable[[], None] = lambda: None,
        on_value_changed: Callable[[str], None] = lambda s: None,
    ) -> None:
        super().__init__(
            font=font,
            position=position,
            width=width,
            default=default,
            disabled=disabled,
            text_align=text_align,
            on_enter=on_enter,
            on_value_changed=on_value_changed,
            sound=GameManager.get_sound("button"),
        )


class StyledSlider(SliderElement):
    def __init__(
        self,
        min_value: float,
        max_value: float,
        position: Position = Position(coords=(0, 0)),
        default_value: float | None = None,
        slider_size: tuple[int, int] = (150, 15),
        knob_size: tuple[int, int] = (10, 30),
        slider_surface: Surface | None = None,
        slider_color: pygame.Color = pygame.Color("white"),
        knob_color: pygame.Color = pygame.Color("white"),
        label: Surface | ButtonElement = pygame.Surface((0,0)),
        label_position: (
            Literal["top"] | Literal["bottom"] | Literal["left"] | Literal["right"]
        ) = "right",
        label_padding: int = 10,
        on_value_change: Callable[[float, str], None] = lambda x, y: None,
        id: str = "",
        show_value: bool = False,
        step: float = 0
    ) -> None:
        super().__init__(
            min_value=min_value,
            max_value=max_value,
            position=position,
            default_value=default_value,
            slider_size=slider_size,
            knob_size=knob_size,
            slider_surface=slider_surface,
            slider_color=slider_color,
            knob_color=knob_color,
            label=label,
            label_position=label_position,
            label_padding=label_padding,
            on_value_changed=on_value_change,
            id=id,
            show_value=show_value,
            step=step,
            sound=GameManager.get_sound("button"),
        )