import math
from pygame import Rect, Color, Surface, transform

from graphics.graphics_manager import get_font
from graphics.outline_text import OutlineText


class Slider:
    value: int
    min: int
    max: int
    rect: Rect
    knob_width: int
    slider_height: int
    slider_surface: Surface
    slider_color: Color
    knob_color: Color
    label: Surface
    
    _label_rect: Rect
    _slider_rect: Rect
    
    def __init__(
        self,
        min_value: int,
        max_value: int,
        rect: Rect,
        default_value: int | None = None,
        knob_width: int | None = None,
        slider_height: int | None = None,
        slider_surface: Surface | None = None,
        slider_color: Color = Color("white"),
        knob_color: Color = Color("red"),
        label: str | Surface = "",
    ) -> None:
        self.min = min_value
        self.max = max_value
        self.rect = rect
        self.value = default_value if default_value is not None else min_value
        self.knob_width = (
            knob_width
            if knob_width is not None
            else min(math.floor(rect.width / 12), 20)
        )
        
        self.slider_height = slider_height if slider_height < rect.height else rect.height
        
        if str is type(label):
            self.label = OutlineText.render(
                text=label,
                font=get_font(rect.height),
                gfcolor=knob_color,
                ocolor=Color("black"),
            )
        else:
            self.label = label
        
        label_rect_mid_right = (rect.midleft[0] - 10, rect.midleft[1])
        self._label_rect = label.get_rect(midright=label_rect_mid_right)
        
        slider_size = (rect[0] - knob_width, self.slider_height)
        if Surface is type(slider_surface):
            self.slider_surface = transform.scale(surface=slider_surface, size=slider_size)   
        else:
            self.slider_surface = Surface(size=slider_size)
            self.slider_surface.fill(slider_color)
        
        self.slider_color = slider_color
        
        self._slider_rect = self.slider_surface.get_rect(center=rect.center)  

    def update(self, surface: Surface) -> None:
        surface.blit(self.label, self._label_rect)
        surface.blit(self.slider_surface, self._slider_rect)
        
        # render knob based on value
        
        # knob_top_left = (,self.rect.top)
        # self._knob_rect
        surface.blit(self.label, self._label_rect)

    def check_for_input(self, mouse_position: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_position)

    def change_value(self, mouse_position: tuple[int, int]):
        if not self.check_for_input():
            return False
        ratio = (mouse_position[0] - self.rect.left) / self.rect.width
        self.value = math.floor(ratio * self.max)
        return True
    
    def _value_to_position(self):
        pass