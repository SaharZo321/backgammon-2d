from pydantic import BaseModel
from pydantic_extra_types.color import Color as PydanticColor
import pygame
from models.player import Player
from typing import Self
from random import randint


class GameState(BaseModel):
    board: list[int]
    bar: dict[Player, int]
    home: dict[Player, int]
    current_turn: Player
    dice: tuple[int, int]
    moves_left: list[int]
    score: dict[Player, int]
    history: list[Self]


class OnlineGameState(GameState):
    online_color: PydanticColor
    local_color: PydanticColor
    history: list[GameState]


def local_to_online(
    game_state: GameState, online_color: PydanticColor, local_color: PydanticColor
) -> OnlineGameState:
    online_game_state = OnlineGameState(
        board=game_state.board,
        bar=game_state.bar,
        home=game_state.home,
        current_turn=game_state.current_turn,
        dice=game_state.dice,
        moves_left=game_state.moves_left,
        score=game_state.score,
        history=game_state.history,
        online_color=online_color,
        local_color=local_color,
    )
    return online_game_state


class ColorConverter:
    @staticmethod
    def pydantic_to_pygame(pydantic_color: PydanticColor) -> pygame.Color:
        rgb = pydantic_color.as_rgb_tuple()
        return pygame.Color(*rgb)

    @staticmethod
    def pygame_to_pydantic(pygame_color: pygame.Color) -> PydanticColor:
        rgb = pygame_color.r, pygame_color.g, pygame_color.b
        return PydanticColor(value=rgb)