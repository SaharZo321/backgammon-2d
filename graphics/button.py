import pygame
from typing import Callable
from graphics.outline_text import OutlineText


class Button():
    _image: pygame.Surface
    _position: tuple[int, int]
    _font: pygame.font.Font
    _base_color: pygame.Color
    _hovering_color: pygame.Color
    _text_input: str
    _text: pygame.Surface
    _outline_size: int
    _outline_color: pygame.Color
    _rect: pygame.Rect 
    _text_rect: pygame.Rect
    _on_click: Callable[[], None]
    
    disabled: bool
    
    def __init__(self,
                 background_image: pygame.Surface | None,
                 position: tuple[int, int],
                 text_input: str,
                 font: pygame.font.Font,
                 base_color: pygame.Color,
                 hovering_color: pygame.Color,
                 outline_size: int = 0,
                 outline_color: pygame.Color = pygame.Color("black"), 
                 on_click: Callable[[], None] = lambda: ()
                 ) -> None:
        
        self.disabled = False
        
        self._position = position
        self._font = font
        self._base_color = base_color
        self._hovering_color = hovering_color
        self._text_input = text_input
        self._outline_size = outline_size
        self._outline_color = outline_color
        self._toggle_text_color(self._base_color)
        self._text_rect = self._text.get_rect(center=(self._position[0], self._position[1]))
        
        if background_image is None:
            self._image = self._text
        
        self._rect = self._image.get_rect(center=(self._position[0], self._position[1]))
    
        self._on_click = on_click
        
    
    def click(self):
        self._on_click()
    
    def update(self, screen: pygame.Surface) -> None:
            
        if self._image is not None:
            screen.blit(self._image, self._rect)
               
        
        
        screen.blit(self._text, self._text_rect)
        
    def check_for_input(self, mouse_position: tuple[int,int]) -> bool:
        if(not self.disabled and mouse_position[0] in range(self._rect.left, self._rect.right) and mouse_position[1] in range(self._rect.top, self._rect.bottom)):
            return True
        return False
    
    def toggle(self, disabled: bool | None = None) -> None:
        if disabled is None:
            self.disabled = not self.disabled
        else:
            self.disabled = disabled
    
    def _toggle_text_color(self, color: pygame.Color):
        
        disabled_color = self._base_color // pygame.Color(2,2,2)
        color = color if not self.disabled else disabled_color
        
        if self._outline_size > 0:
            self._text = OutlineText.render(text=self._text_input, font=self._font, gfcolor=color, ocolor=self._outline_color, opx=self._outline_size)
        else:
            self._text = self._font.render(self._text_input, True, color)
    
    def check_hover(self, mouse_position: tuple[int,int]) -> None:
        color = self._hovering_color if self.check_for_input(mouse_position=mouse_position) else self._base_color
        self._toggle_text_color(color)
        
        
    