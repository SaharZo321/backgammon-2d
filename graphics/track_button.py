import pygame
from typing import Callable

import pygame.gfxdraw


class TrackButton():
    rect: pygame.Rect
    highlighted: bool
    is_top: bool
    
    def __init__(self, rect: pygame.Rect, is_top: bool) -> None:
        self.rect = rect
        self.is_top = is_top
        self.highlighted = False
    
    def update(self, screen: pygame.Surface) -> None:
        
        if self.highlighted:
            padding = 3
            height = 10
            width = self.rect.width - padding * 2
            top = self.rect.top - height - padding if self.is_top else self.rect.bottom + padding
            active_rect = pygame.Rect(self.rect.left + padding, top, width, height)
            pygame.draw.rect(surface=screen, color=(0,150,250), rect=active_rect,width=0, border_radius=2)
      
    def check_for_input(self, mouse_position: tuple[int,int]) -> bool:
        if(mouse_position[0] in range(self.rect.left, self.rect.right) and mouse_position[1] in range(self.rect.top, self.rect.bottom)):
            return True
        return False
    
