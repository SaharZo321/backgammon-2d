from pydantic import BaseModel
from enum import Enum

class MoveType(Enum):
    leave_bar = 1
    normal_move = 2
    bear_off = 3


class Move(BaseModel):
    move_type: MoveType
    start: int
    end: int
    