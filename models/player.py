from enum import Enum
from typing import Self


class Player(Enum):
    player1 = "player1"
    player2 = "player2"

    @classmethod
    def other(cls, player: Self) -> Self:
        return cls.player2 if player == cls.player1 else cls.player1
