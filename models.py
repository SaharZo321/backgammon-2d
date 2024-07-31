from enum import StrEnum, auto
from typing import Literal
from pydantic import BaseModel, Field, ValidationInfo, field_validator
from pydantic_extra_types.color import Color as PydanticColor
import pygame


class Address(BaseModel):
    ip_address: str
    port: int


class Player(StrEnum):
    player1 = auto()
    player2 = auto()

    @classmethod
    def other(cls, player: type["Player"]):
        return cls.player2 if player == cls.player1 else cls.player1


class GameState(BaseModel):
    board: list[int]
    bar: dict[Player, int]
    home: dict[Player, int]
    current_turn: Player
    dice: tuple[int, int]
    moves_left: list[int]
    score: dict[Player, int]

    def to_online_game_state(
        self,
        online_color: PydanticColor,
        local_color: PydanticColor,
        history_length: int,
    ):
        dump = self.model_dump()

        return OnlineGameState(
            **dump,
            online_color=online_color,
            local_color=local_color,
            history_length=history_length,
        )

    def is_board_equal(self, state: type["GameState"]):
        return all(
            [track == state.board[index] for index, track in enumerate(self.board)]
        )


class OnlineGameState(GameState):
    history_length: int
    online_color: PydanticColor
    local_color: PydanticColor


class MoveType(StrEnum):
    leave_bar = auto()
    normal_move = auto()
    bear_off = auto()


class Move(BaseModel):
    move_type: MoveType
    start: int
    end: int


class ScoredMoves(BaseModel):
    moves: list[Move]
    score: int


class ServerFlags(StrEnum):
    leave = auto()
    get_current_state = auto()
    done = auto()
    undo = auto()


class Position(BaseModel):
    anchor: Literal[
        "topleft",
        "bottomleft",
        "topright",
        "bottomright",
        "midtop",
        "midleft",
        "midbottom",
        "midright",
        "center",
    ] = Field(default="center")
    coords: tuple[int, int] = Field(default=(0, 0))

    def dump(self):
        return {self.anchor: self.coords}


class Options(BaseModel):
    ip: str
    opponent_color: PydanticColor
    piece_color: PydanticColor
    volume: float
    mute_volume: float

    @field_validator("volume", "mute_volume")
    @classmethod
    def check_volume(cls, value: float, info: ValidationInfo):
        if isinstance(value, float):
            between_zero_and_one = 0 <= value <= 1
            assert between_zero_and_one, f"{info.field_name} must be between 0 and 1"
        return value


class ColorConverter:
    @staticmethod
    def pydantic_to_pygame(pydantic_color: PydanticColor) -> pygame.Color:
        rgb = pydantic_color.as_rgb_tuple()
        return pygame.Color(*rgb)

    @staticmethod
    def pygame_to_pydantic(pygame_color: pygame.Color) -> PydanticColor:
        rgb = pygame_color.r, pygame_color.g, pygame_color.b
        return PydanticColor(value=rgb)
