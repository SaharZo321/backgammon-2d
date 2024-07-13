import pygame
import pygame.gfxdraw
import math
from config import RESOLUTION, BACKGROUND
from graphics.track_button import TrackButton
from models.player import Player

screen_width, screen_height = RESOLUTION

def get_font(size, bold=False, italic=False) -> pygame.font.Font:
    return pygame.font.SysFont("Cooper Black", size, bold, italic)


def get_mid_width() -> int:
    return screen_width / 2



class GraphicsManager():
    screen: pygame.Surface
    top_tracks_rect: list[pygame.Rect]
    bottom_tracks_rect: list[pygame.Rect]
    tracks: list[TrackButton]
    home_tracks = dict[Player, TrackButton]
    player_colors: dict[Player, pygame.Color]
    
    SIZE = screen_height
    SIDE_PADDING = (screen_width - screen_height) / 2
    TRIANGLE_HEIGHT = math.floor(SIZE * 0.4)
    BOARD_PADDING = SIZE * 0.03
    SIDE_DIMENSIONS = (SIZE / 2 - 2 * BOARD_PADDING, SIZE - 2 * BOARD_PADDING)
    LEFT_SIDE_POSITION = (SIDE_PADDING + BOARD_PADDING, BOARD_PADDING)
    RIGHT_SIDE_POSITION = (SIDE_PADDING + SIZE / 2 + BOARD_PADDING, BOARD_PADDING)
    LEFT_SIDE_RECT = pygame.Rect(LEFT_SIDE_POSITION + SIDE_DIMENSIONS)
    RIGHT_SIDE_RECT = pygame.Rect(RIGHT_SIDE_POSITION + SIDE_DIMENSIONS)
    MINI_RECT = pygame.Rect(0,0, math.floor(LEFT_SIDE_RECT.width / 6), TRIANGLE_HEIGHT)
    HOME_RECT = pygame.Rect(SIDE_PADDING - screen_width * 0.05,0,screen_width * 0.05,screen_height)
    HOME_TRACK_PADDING = HOME_RECT.width * 0.15
    HOME_TRACK_WIDTH = HOME_RECT.width - 2 * HOME_TRACK_PADDING
    HOME_TRACK_HEIGHT = screen_height * 0.4
    HOME_TRACK_TOP_RECT = pygame.Rect(HOME_RECT.left + HOME_TRACK_PADDING, HOME_RECT.top + HOME_TRACK_PADDING * 2, HOME_TRACK_WIDTH, HOME_TRACK_HEIGHT)
    HOME_TRACK_BOTTOM_RECT = pygame.Rect(HOME_RECT.left + HOME_TRACK_PADDING, HOME_RECT.bottom - HOME_TRACK_PADDING * 2 - HOME_TRACK_HEIGHT, HOME_TRACK_WIDTH, HOME_TRACK_HEIGHT)
    
    
    def __init__(self, screen: pygame.Surface, player1_color: pygame.Color, player2_color: pygame.Color) -> None:
        self.screen = screen
        self.player_colors = {
            Player.player1: player1_color,
            Player.player2: player2_color
        }
        self.top_tracks_rect = []
        self.bottom_tracks_rect = []
        self.tracks = []
        
        self.create_tracks_rects()
        self.create_home_tracks()
    
    def create_home_tracks(self) -> None:
        #top player 2
        self.home_tracks = {
            Player.player2: TrackButton(rect=self.HOME_TRACK_TOP_RECT,is_top=True),
            Player.player1: TrackButton(rect=self.HOME_TRACK_BOTTOM_RECT,is_top=False)
        }
            
    def toggle_home_track_button(self, player: Player, highlight: bool = True) -> None:
        self.home_tracks[player].highlighted = highlight
    
    def toggle_track_button(self, index: int, highlight: bool = True) -> None:
        self.tracks[index].highlighted = highlight
     
    def highlight_tracks(self, highlighted_indexes: list[int]) -> None:
        self.home_tracks[Player.player1].highlighted = any(index > 23 for index in highlighted_indexes)
        self.home_tracks[Player.player2].highlighted = any(index < 0 for index in highlighted_indexes)
        
        for index, button in enumerate(self.tracks):
            
            if index in highlighted_indexes:
                button.highlighted = True
            else:
                button.highlighted = False
       
    def check_tracks_input(self, mouse_position: tuple[int,int]) -> bool:
        for index, button in enumerate(self.tracks): 
            if self.check_track_input(mouse_position=mouse_position, index=index):
                return True
                
        return False
    
    def check_track_input(self, mouse_position: tuple[int,int], index: int) -> bool:
        button = self.tracks[index]
        return button.check_for_input(mouse_position) and button.highlighted
       
    
    def check_home_track_input(self, mouse_position: tuple[int,int], player: Player) -> bool:
        button = self.home_tracks[player]
        return button.check_for_input(mouse_position) and button.highlighted
    
    def create_tracks_rects(self) -> None:
        
        # top left RECT
        for i in range(6):
            NEW_RECT_POS = (self.LEFT_SIDE_RECT.left + i * self.MINI_RECT.width, self.LEFT_SIDE_RECT.top)
            rect = pygame.Rect(NEW_RECT_POS, self.MINI_RECT.size)
            self.top_tracks_rect.append(rect)
            self.tracks.append(TrackButton(rect=rect,is_top=True))
            
        # top right RECT
        for i in range(6):
            NEW_RECT_POS = (self.RIGHT_SIDE_RECT.left + i * self.MINI_RECT.width, self.RIGHT_SIDE_RECT.top)
            rect = pygame.Rect(NEW_RECT_POS, self.MINI_RECT.size)
            self.top_tracks_rect.append(rect)
            self.tracks.append(TrackButton(rect=rect,is_top=True))
            
        # bottom right RECT
        for i in range(6):
            NEW_RECT_POS = (self.RIGHT_SIDE_RECT.right - (i + 1) * self.MINI_RECT.width, self.RIGHT_SIDE_RECT.bottom - self.MINI_RECT.height)
            rect = pygame.Rect(NEW_RECT_POS, self.MINI_RECT.size)
            self.bottom_tracks_rect.append(rect)
            self.tracks.append(TrackButton(rect=rect,is_top=False))
        
        # bottom left RECT
        for i in range(6):
            NEW_RECT_POS = (self.LEFT_SIDE_RECT.right - (i + 1) * self.MINI_RECT.width, self.LEFT_SIDE_RECT.bottom - self.MINI_RECT.height)
            rect = pygame.Rect(NEW_RECT_POS, self.MINI_RECT.size)
            self.bottom_tracks_rect.append(rect)
            self.tracks.append(TrackButton(rect=rect,is_top=False))
    
    def render_piece(self, center: tuple[int,int], color: pygame.Color, radius: int):
        pygame.gfxdraw.filled_circle(self.screen, center[0], center[1], radius, color)
        pygame.gfxdraw.aacircle(self.screen, center[0], center[1], radius, (0,0,0))
        pygame.gfxdraw.aacircle(self.screen, center[0], center[1], math.floor(radius / 2), (0,0,0))
        
    def render_board(self, board: list[int], bar: dict[Player, int], home: dict[Player, int]):
        
        pygame.draw.rect(self.screen, "brown", (self.SIDE_PADDING, 0, self.SIZE, self.SIZE))
        
        side_color = pygame.Color(246,224,135)
        pygame.draw.rect(self.screen, side_color, self.LEFT_SIDE_POSITION + self.SIDE_DIMENSIONS)
        pygame.draw.rect(self.screen, "black", self.LEFT_SIDE_POSITION + self.SIDE_DIMENSIONS, 2)
        
        pygame.draw.rect(self.screen, side_color, self.RIGHT_SIDE_POSITION + self.SIDE_DIMENSIONS)
        pygame.draw.rect(self.screen, "black", self.RIGHT_SIDE_POSITION + self.SIDE_DIMENSIONS, 2)
        
        self.render_tracks()
        
          
        all_rect = self.top_tracks_rect + self.bottom_tracks_rect
        for index, pieces in enumerate(board):
            player = Player.player1 if pieces > 0 else Player.player2
            color = self.player_colors[player]
            self.render_track_pieces(all_rect[index], color, abs(pieces), index < 12)
            
        for button in self.tracks:
            button.update(self.screen)
        
        self.render_bar_pieces(bar=bar)
        
        self.render_home(home=home)
    
    def render_tracks(self) -> None:
        for index, rect in enumerate(self.top_tracks_rect):
            first = rect.topleft
            second = rect.topright
            third = (math.floor((rect.right + rect.left) / 2), rect.bottom)
            color = (0,0,0) if index % 2 == 0 else (150,0,0)
            pygame.gfxdraw.filled_polygon(self.screen, (first, second, third), color)
            pygame.gfxdraw.aapolygon(self.screen, (first, second, third), (0,0,0))
            
        for index, rect in enumerate(self.bottom_tracks_rect):
            first = rect.bottomleft
            second = rect.bottomright
            third = (math.floor((rect.right + rect.left) / 2), rect.top)
            color = (0,0,0) if index % 2 == 0 else (150,0,0)
            pygame.gfxdraw.filled_polygon(self.screen, (first, second, third), color)
            pygame.gfxdraw.aapolygon(self.screen, (first, second, third), (0,0,0))
                
    def render_track_pieces(self, rect: pygame.Rect, color: pygame.Color, number: int, is_top: bool):
        radius = math.floor(rect.width * 0.45)
        for i in range(number):
            new_y = (rect.top + radius * (2 * i + 1)) if is_top else (rect.bottom - radius * (2 * i + 1))
            center = (rect.centerx, new_y)
            self.render_piece(center, color, radius)
            
    def render_bar_pieces(self, bar: dict[Player, int]):
        #player1
        color = self.player_colors[Player.player1]
        radius = math.floor(self.BOARD_PADDING * 1.1)
        number = bar[Player.player1]
        for counter in range(number):
            counter_center = (math.floor(screen_width / 2), math.floor((screen_height / 4 - radius * number) + (counter * 2 + 1) * radius))
            self.render_piece(counter_center, color, radius)
        
        #player2 
        color = self.player_colors[Player.player2]
        radius = math.floor(self.BOARD_PADDING * 1.1)
        number = bar[Player.player2]
        for counter in range(number):
            counter_center = (math.floor(screen_width / 2), math.floor((screen_height / 4 * 3 - radius * number) + (counter * 2 + 1) * radius))
            self.render_piece(counter_center, color, radius)

    def render_home(self, home: dict[Player, int]) -> None:
        pygame.draw.rect(surface=self.screen, color="brown", rect=self.HOME_RECT)
        pygame.draw.rect(surface=self.screen, color="black", rect=self.HOME_RECT, width=2)
        pygame.draw.rect(surface=self.screen, color="black", rect=self.HOME_RECT, width=2)
        
        
        
        #top home rect player 2
        pygame.draw.rect(surface=self.screen, color="black", rect=self.HOME_TRACK_TOP_RECT, width=0, border_radius=3)
        
        #bottom home rect player 1
        pygame.draw.rect(surface=self.screen, color="black", rect=self.HOME_TRACK_BOTTOM_RECT, width=0, border_radius=3)
        
        piece_height = self.HOME_TRACK_TOP_RECT.height / 15
        piece_width = self.HOME_TRACK_TOP_RECT.width
        #render top pieces
        player = Player.player2
        self.home_tracks[player].update(screen=self.screen)
        for piece in range(home[player]):
            color = self.player_colors[player]
            top = self.HOME_TRACK_TOP_RECT.top + piece * piece_height
            left = self.HOME_TRACK_TOP_RECT.left
            rect = pygame.Rect(left, top, piece_width, piece_height)
            pygame.draw.rect(surface=self.screen, color=color, rect=rect, width=0, border_radius=2)
            pygame.draw.rect(surface=self.screen, color="black", rect=rect, width=1, border_radius=2)
        
        #render bottom pieces
        player = Player.player1
        self.home_tracks[player].update(screen=self.screen)
        for piece in range(home[player]):
            color = self.player_colors[player]
            top = self.HOME_TRACK_BOTTOM_RECT.bottom - (piece + 1) * piece_height
            left = self.HOME_TRACK_BOTTOM_RECT.left
            rect = pygame.Rect(left, top, piece_width, piece_height)
            pygame.draw.rect(surface=self.screen, color=color, rect=rect, width=0, border_radius=2)
            pygame.draw.rect(surface=self.screen, color="black", rect=rect, width=1, border_radius=2)

    @staticmethod
    def render_background(screen: pygame.Surface):
        screen.blit(BACKGROUND, (0,0))
        