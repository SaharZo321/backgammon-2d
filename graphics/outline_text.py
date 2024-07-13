import pygame


class OutlineText():
    _circle_cache: dict[int, list[tuple[int,int]]]= {}
    
    @classmethod
    def _circlepoints(cls, radius: float):
        radius = int(round(radius))
        if radius in cls._circle_cache:
            return cls._circle_cache[radius]
        x, y, e = radius, 0, 1 - radius
        cls._circle_cache[radius] = points = []
        while x >= y:
            points.append((x, y))
            y += 1
            if e < 0:
                e += 2 * y - 1
            else:
                x -= 1
                e += 2 * (y - x) - 1
        points += [(y, x) for x, y in points if x > y]
        points += [(-x, y) for x, y in points if x]
        points += [(x, -y) for x, y in points if y]
        points.sort()
        return points
    
    @classmethod
    def render(cls, text: str, font: pygame.font.Font, gfcolor: pygame.Color=pygame.Color('dodgerblue'), ocolor: pygame.Color=pygame.Color(255, 255, 255), opx: int=2) -> pygame.Surface:
        textsurface = font.render(text, True, gfcolor).convert_alpha()
        w = textsurface.get_width() + 2 * opx
        h = font.get_height()

        osurf = pygame.Surface((w, h + 2 * opx)).convert_alpha()
        osurf.fill((0, 0, 0, 0))

        surf = osurf.copy()

        osurf.blit(font.render(text, True, ocolor).convert_alpha(), (0, 0))

        for dx, dy in cls._circlepoints(opx):
            surf.blit(osurf, (dx + opx, dy + opx))

        surf.blit(textsurface, (opx, opx))
        return surf