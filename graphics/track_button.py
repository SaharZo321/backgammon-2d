import pygame
from typing import Callable

import pygame.gfxdraw


class TrackButton:
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
