from enum import Enum
from typing import Self
from pydantic import BaseModel

from pydantic_extra_types.color import Color as PydanticColor


class Address(BaseModel):
    ip_address: str
    port: int


class Player(Enum):
    player1 = 1
    player2 = -1

    @classmethod
    def other(cls, player: Self) -> Self:
        return cls.player2 if player == cls.player1 else cls.player1


class GameState(BaseModel):
    board: list[int]
    bar: dict[Player, int]
    home: dict[Player, int]
    current_turn: Player
    dice: tuple[int, int]
    moves_left: list[int]
    score: dict[Player, int]
    history: list[Self]

    def to_online(
        self, online_color: PydanticColor, local_color: PydanticColor
    ):
        attributes = self.model_dump()
        attributes["online_color"] = online_color
        attributes["local_color"] = local_color

        return OnlineGameState(**attributes)


class OnlineGameState(GameState):
    online_color: PydanticColor
    local_color: PydanticColor
    history: list[GameState]
    

class MoveType(Enum):
    leave_bar = 1
    normal_move = 2
    bear_off = 3


class Move(BaseModel):
    move_type: MoveType
    start: int
    end: int


class ScoredMoves(BaseModel):
    moves: list[Move]
    score: int
