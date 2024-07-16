from pydantic import BaseModel
from models.player import Player
from typing import Self

class GameState(BaseModel):
    board: list[int]
    bar: dict[Player, int]
    home: dict[Player, int]
    current_turn: Player
    dice: tuple[int,int]
    moves_left: list[int]
    score: dict[Player, int]
    history: list[Self]