import math
from typing import Callable, Literal
import pygame
from config import get_font
from graphics.outline_text import OutlineText


class Element:
    rect: pygame.Rect
    disabled: bool
    
    def __init__(self) -> None:
        pass
        raise NotImplementedError()

    def render(self, surface: pygame.Surface) -> None:
        pass
        raise NotImplementedError()

    def update(
        self, events: list[pygame.event.Event]
    ) -> None:
        """
        Updates the element properties. Ususally implemented with is_input_recieved.
        """
        pass

    def click(self):
        pass
    
    def is_input_recieved(self) -> bool:
        mouse_position = pygame.mouse.get_pos()
        if not self.disabled and self.rect.collidepoint(mouse_position):
            return True
        return False

type RelativePosition = Literal["top", "bottom", "left", "right"]


class SliderElement(Element):
    value: int
    min: int
    max: int
    rect: pygame.Rect
    knob_width: int
    slider_height: int
    slider_surface: pygame.Surface
    slider_color: pygame.Color
    knob_color: pygame.Color
    label: pygame.Surface
    label_position: RelativePosition
    label_padding: int
    on_value_changed: Callable[[int, str], None]
    id: str

    _label_rect: pygame.Rect
    _slider_rect: pygame.Rect

    def __init__(
        self,
        min_value: int,
        max_value: int,
        rect: pygame.Rect,
        default_value: int | None = None,
        knob_width: int | None = None,
        slider_height: int | None = None,
        slider_surface: pygame.Surface | None = None,
        slider_color: pygame.Color = pygame.Color("white"),
        knob_color: pygame.Color = pygame.Color("white"),
        label: str | pygame.Surface = "",
        label_position: RelativePosition = "left",
        label_padding: int = 10,
        label_color: pygame.Color = pygame.Color("white"),
        on_value_changed: Callable[[int, str], None] = lambda x: None,
        id: str = "",
    ) -> None:
        self.id = id
        self.on_value_changed = on_value_changed
        self.min = min_value
        self.max = max_value
        self.rect = rect
        self.value = default_value if default_value is not None else min_value
        self.knob_width = (
            knob_width
            if knob_width is not None
            else min(math.floor(rect.width / 12), 20)
        )
        self.knob_color = knob_color
        self.slider_height = (
            slider_height
            if slider_height is not None and slider_height < rect.height
            else rect.height / 3
        )
        self.disabled = False

        if type(label) is str:
            self.label = OutlineText.render(
                text=label,
                font=get_font(math.floor(rect.height * 0.8)),
                gfcolor=label_color,
                ocolor=pygame.Color("black"),
            )
        else:
            self.label = label
        self.label_padding = label_padding
        self.set_label_position(label_position)

        slider_size = (self.rect.width - self.knob_width, self.slider_height)
        if type(slider_surface) is pygame.Surface:
            self.slider_surface = pygame.transform.scale(slider_surface, slider_size)
        else:
            self.slider_surface = pygame.Surface(slider_size)
            self.slider_surface.fill(slider_color)
            pygame.draw.rect(self.slider_surface, "black", (0, 0) + (slider_size), 2)

        self.slider_color = slider_color

        self._slider_rect = self.slider_surface.get_rect(center=rect.center)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.label, self._label_rect)
        surface.blit(self.slider_surface, self._slider_rect)
        surface.blit(self.label, self._label_rect)
        # render knob based on value
        knob_surface = pygame.Surface(size=(self.knob_width, self.rect.height))
        knob_center = self._value_to_position(self.value)
        # print(knob_center)
        knob_rect = knob_surface.get_rect(center=knob_center)
        pygame.draw.rect(surface, self.knob_color, knob_rect)
        pygame.draw.rect(surface, pygame.Color("black"), knob_rect, width=2)

    def click(self):
        print("clicked")

        if self.is_input_recieved():
            mouse_position = pygame.mouse.get_pos()
            value = self._position_to_value(mouse_position)
            self.set_value(value)

    def update(
        self, events: list[pygame.event.Event]
    ) -> None:
        mouse_position = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and self.is_input_recieved():
            value = self._position_to_value(mouse_position)
            self.set_value(value)

    def _value_to_position(self, value: int):
        ratio = value / self.max
        centerx = ratio * self._slider_rect.width + self._slider_rect.left
        return (centerx, self._slider_rect.centery)

    def _position_to_value(self, mouse_position: tuple[int, int]):
        ratio = (mouse_position[0] - self._slider_rect.left) / self._slider_rect.width
        return math.floor(ratio * self.max)

    def set_value(self, value: int):
        value = max(value, self.min) if value < self.min else min(value, self.max)
        self.on_value_changed(value, self.id)
        self.value = value

    def set_label_position(self, position: RelativePosition):

        self.label_position = position

        match position:
            case "left":
                label_rect_midright = (
                    self.rect.midleft[0] - self.label_padding,
                    self.rect.midleft[1],
                )
                self._label_rect = self.label.get_rect(midright=label_rect_midright)
            case "right":
                label_rect_midleft = (
                    self.rect.midright[0] + self.label_padding,
                    self.rect.midright[1],
                )
                self._label_rect = self.label.get_rect(midleft=label_rect_midleft)
            case "top":
                label_rect_midbottom = (
                    self.rect.midtop[0],
                    self.rect.midtop[1] - self.label_padding,
                )
                self._label_rect = self.label.get_rect(midbottom=label_rect_midbottom)
            case "bottom":
                label_rect_midtop = (
                    self.rect.midbottom[0],
                    self.rect.midbottom[1] + self.label_padding,
                )
                self._label_rect = self.label.get_rect(midtop=label_rect_midtop)


class ButtonElement(Element):
    image: pygame.Surface
    position: tuple[int, int]
    disabled: bool
    text_input: str

    _font: pygame.font.Font
    _base_color: pygame.Color
    _hovering_color: pygame.Color
    _text: pygame.Surface
    _outline_size: int
    _outline_color: pygame.Color
    rect: pygame.Rect
    _text_rect: pygame.Rect
    _on_click: Callable[[], None]

    def __init__(
        self,
        background_image: pygame.Surface | None,
        position: tuple[int, int],
        text_input: str,
        font: pygame.font.Font,
        base_color: pygame.Color = pygame.Color("red"),
        hovering_color: pygame.Color = pygame.Color("white"),
        outline_size: int = 1,
        outline_color: pygame.Color = pygame.Color("black"),
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

        self.rect = self.image.get_rect(center=(self.position[0], self.position[1]))
        self._on_click = on_click

    def click(self):
        mouse_position = pygame.mouse.get_pos()
        if self.is_input_recieved():
            self._on_click()

    def render(self, screen: pygame.Surface) -> None:
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self._text, self._text_rect)

    def toggle(self, disabled: bool | None = None) -> None:
        if disabled is None:
            self.disabled = not self.disabled
        else:
            self.disabled = disabled

    def _toggle_text_color(self, color: pygame.Color):

        disabled_color = self._base_color // pygame.Color(2, 2, 2)
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

    def update(self, events: list[pygame.event.Event]) -> None:
        color = self._hovering_color if self.is_input_recieved() else self._base_color
        self._toggle_text_color(color)


class BetterButtonElement(ButtonElement):
    position: tuple[int, int]
    disabled: bool
    text_input: str
    text_color: pygame.Color
    base_color: pygame.Color
    hovering_color: pygame.Color
    text_outline_size: int
    text_outline_color: pygame.Color
    rect: pygame.Rect
    
    _border_radius: int
    _displayed_color: pygame.Color
    _displayed_outline_color: pygame.Color
    _font: pygame.font.Font
    _text: pygame.Surface
    _outline_size: int
    outline_color: pygame.Color

    _text_rect: pygame.Rect
    _on_click: Callable[[], None]

    def __init__(
        self,
        position: tuple[int, int],
        text_input: str,
        font: pygame.font.Font,
        text_color: pygame.Color = pygame.Color("black"),
        text_outline_size: int = 0,
        text_outline_color: pygame.Color = pygame.Color("white"),
        base_color: pygame.Color = pygame.Color("red"),
        hovering_color: pygame.Color = pygame.Color("white"),
        outline_size: int = 3,
        outline_color: pygame.Color = pygame.Color("black"),
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
        scalex = (
            (self._text_rect.height * scaley - self._text_rect.height) * 4
            + self._text_rect.width
        ) / self._text_rect.width
        self.rect = self._text_rect.scale_by(scalex, scaley)
        self._on_click = on_click

    def render(self, screen: pygame.Surface) -> None:
        br = (
            self._border_radius
            if self._border_radius is not None
            else math.floor(self.rect.height / 4)
        )
        pygame.draw.rect(
            surface=screen,
            color=self._displayed_color,
            rect=self.rect,
            border_radius=br,
        )
        pygame.draw.rect(
            surface=screen,
            color=self._displayed_outline_color,
            rect=self.rect,
            width=self._outline_size,
            border_radius=br,
        )
        screen.blit(self._text, self._text_rect)

    def _toggle_color(self, is_hovering: bool):
        disabled_color = self.base_color // pygame.Color(2, 2, 2)
        disabled_outline_color = self.outline_color // pygame.Color(2, 2, 2)
        disabled_text_color = self.text_color // pygame.Color(2, 2, 2)
        disabled_text_outline_color = self.text_outline_color // pygame.Color(2, 2, 2)

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

    def update(self, events: list[pygame.event.Event]) -> None:
        self._toggle_color(self.is_input_recieved())


class TrackButtonElement(Element):
    rect: pygame.Rect
    highlighted: bool
    is_top: bool
    surface: pygame.Surface
    surface_rect: pygame.Rect

    def __init__(
        self,
        rect: pygame.Rect,
        is_top: bool,
        surface: pygame.Surface,
        surface_rect: pygame.Rect,
    ) -> None:
        self.rect = rect
        self.is_top = is_top
        self.highlighted = False
        self.surface = surface
        self.surface_rect = surface_rect
        self.disabled = False

    def render(self) -> None:

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

    def is_input_recieved(self) -> bool:
        mouse_position = pygame.mouse.get_pos()
        
        return mouse_position[0] - self.surface_rect.left in range(
            self.rect.left, self.rect.right
        ) and mouse_position[1] + self.surface_rect.top in range(
            self.rect.top, self.rect.bottom
        )
