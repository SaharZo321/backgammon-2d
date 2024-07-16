import pygame
from pygame import Color
from typing import Callable
from graphics.outline_text import OutlineText
import math


class Button:
    position: tuple[int, int]
    disabled: bool
    text_input: str
    text_color: Color
    base_color: Color
    hovering_color: Color
    text_outline_size: int
    text_outline_color: Color

    _border_radius: int
    _displayed_color: Color
    _displayed_outline_color: Color
    _font: pygame.font.Font
    _text: pygame.Surface
    _outline_size: int
    outline_color: Color
    _rect: pygame.Rect
    _text_rect: pygame.Rect
    _on_click: Callable[[], None]

    def __init__(
        self,
        # background_image: pygame.Surface | None,
        position: tuple[int, int],
        text_input: str,
        font: pygame.font.Font,
        text_color: Color = Color("black"),
        text_outline_size: int = 0,
        text_outline_color: Color = Color("white"),
        base_color: Color = Color("red"),
        hovering_color: Color = Color("white"),
        outline_size: int = 3,
        outline_color: Color = Color("black"),
        border_radius: int | None = None,
        on_click: Callable[[], None] = lambda: (),
    ) -> None:

        self._border_radius = border_radius
        self.disabled = False
        self.text_color = text_color
        self.position = position
        self.text_outline_color = text_outline_color
        self.text_outline_size = text_outline_size
        self._font = font
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.text_input = text_input
        self._outline_size = outline_size
        self.outline_color = outline_color
        self._toggle_color(False)
        self._text_rect = self._text.get_rect(
            center=(self.position[0], self.position[1])
        )
        scaley = 1.1
        scalex = ((self._text_rect.height*scaley - self._text_rect.height)*4 + self._text_rect.width) / self._text_rect.width
        self._rect = self._text_rect.scale_by(scalex, scaley)
        self._on_click = on_click

    def click(self):
        self._on_click()

    def update(self, screen: pygame.Surface) -> None:
        br = (
            self._border_radius
            if self._border_radius is not None
            else math.floor(self._rect.height / 4)
        )
        pygame.draw.rect(
            surface=screen,
            color=self._displayed_color,
            rect=self._rect,
            border_radius=br,
        )
        pygame.draw.rect(
            surface=screen,
            color=self._displayed_outline_color,
            rect=self._rect,
            width=self._outline_size,
            border_radius=br,
        )
        screen.blit(self._text, self._text_rect)

    def check_for_input(self, mouse_position: tuple[int, int]) -> bool:
        if (
            not self.disabled
            and mouse_position[0] in range(self._rect.left, self._rect.right)
            and mouse_position[1] in range(self._rect.top, self._rect.bottom)
        ):
            return True
        return False

    def toggle(self, disabled: bool | None = None) -> None:
        if disabled is None:
            self.disabled = not self.disabled
        else:
            self.disabled = disabled

    def _toggle_color(self, is_hovering: bool):
        disabled_color = self.base_color // Color(2, 2, 2)
        disabled_outline_color = self.outline_color // Color(2, 2, 2)
        disabled_text_color = self.text_color // Color(2, 2, 2)
        disabled_text_outline_color = self.text_outline_color // Color(2, 2, 2)

        color = self.hovering_color if is_hovering else self.base_color
        self._displayed_color = color if not self.disabled else disabled_color
        self._displayed_outline_color = (
            self.outline_color if not self.disabled else disabled_outline_color
        )
        text_color = self.text_color if not self.disabled else disabled_text_color
        text_outline_color = (
            self.text_outline_color
            if not self.disabled
            else disabled_text_outline_color
        )
        if self._outline_size > 0:
            self._text = OutlineText.render(
                text=self.text_input,
                font=self._font,
                gfcolor=text_color,
                ocolor=text_outline_color,
                opx=self.text_outline_size,
            )
        else:
            self._text = self._font.render(self.text_input, True, text_color)

    def change_color(self, mouse_position: tuple[int, int]) -> None:
        self._toggle_color(self.check_for_input(mouse_position=mouse_position))
