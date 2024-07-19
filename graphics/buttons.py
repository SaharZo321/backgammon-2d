import pygame
from pygame import Color
from typing import Callable
from graphics.outline_text import OutlineText
import math





class Button:
    image: pygame.Surface
    position: tuple[int, int]
    disabled: bool
    text_input: str

    _font: pygame.font.Font
    _base_color: Color
    _hovering_color: Color
    _text: pygame.Surface
    _outline_size: int
    _outline_color: Color
    _rect: pygame.Rect
    _text_rect: pygame.Rect
    _on_click: Callable[[], None]


    def __init__(
        self,
        background_image: pygame.Surface | None,
        position: tuple[int, int],
        text_input: str,
        font: pygame.font.Font,
        base_color: Color = Color("red"),
        hovering_color: Color = Color("white"),
        outline_size: int = 1,
        outline_color: Color = Color("black"),
        on_click: Callable[[], None] = lambda: (),
    ) -> None:

        self.disabled = False

        self.position = position
        self._font = font
        self._base_color = base_color
        self._hovering_color = hovering_color
        self.text_input = text_input
        self._outline_size = outline_size
        self._outline_color = outline_color
        self._toggle_text_color(self._base_color)
        self._text_rect = self._text.get_rect(
            center=(self.position[0], self.position[1])
        )
        self._text = font.render(self.text_input, True, base_color)
        self.image = background_image
        if background_image is None:
            self.image = self._text

        self._rect = self.image.get_rect(center=(self.position[0], self.position[1]))
        self._on_click = on_click

    def click(self):
        self._on_click()

    def update(self, screen: pygame.Surface) -> None:
        if self.image is not None:
            screen.blit(self.image, self._rect)
        screen.blit(self._text, self._text_rect)

    def check_for_input(self, mouse_position: tuple[int, int]) -> bool:
        if (
            not self.disabled
            and self._rect.collidepoint(mouse_position)
        ):
            return True
        return False

    def toggle(self, disabled: bool | None = None) -> None:
        if disabled is None:
            self.disabled = not self.disabled
        else:
            self.disabled = disabled

    def _toggle_text_color(self, color: Color):

        disabled_color = self._base_color // Color(2, 2, 2)
        color = color if not self.disabled else disabled_color

        if self._outline_size > 0:
            self._text = OutlineText.render(
                text=self.text_input,
                font=self._font,
                gfcolor=color,
                ocolor=self._outline_color,
                opx=self._outline_size,
            )
        else:
            self._text = self._font.render(self.text_input, True, color)

    def change_color(self, mouse_position: tuple[int, int]) -> None:
        color = (
            self._hovering_color
            if self.check_for_input(mouse_position=mouse_position)
            else self._base_color
        )
        self._toggle_text_color(color)


class BetterButton(Button):
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


class TrackButton():
    rect: pygame.Rect
    highlighted: bool
    is_top: bool
    surface: pygame.Surface
    surface_rect: pygame.Rect

    def __init__(self, rect: pygame.Rect, is_top: bool, surface: pygame.Surface, surface_rect: pygame.Rect) -> None:
        self.rect = rect
        self.is_top = is_top
        self.highlighted = False
        self.surface = surface
        self.surface_rect = surface_rect

    def update(self) -> None:

        if self.highlighted:
            padding = 3
            height = 10
            width = self.rect.width - padding * 2
            top = (
                self.rect.top - height - padding
                if self.is_top
                else self.rect.bottom + padding
            )
            active_rect = pygame.Rect(self.rect.left + padding, top, width, height)
            pygame.draw.rect(
                surface=self.surface,
                color=(0, 150, 250),
                rect=active_rect,
                width=0,
                border_radius=2,
            )

    def check_for_input(self, mouse_position: tuple[int, int]) -> bool:
        if mouse_position[0] - self.surface_rect.left in range(
            self.rect.left, self.rect.right
        ) and mouse_position[1] + self.surface_rect.top in range(self.rect.top, self.rect.bottom):
            return True
        return False
