from pydantic import BaseModel
from models.move import Move

class ScoredMoves(BaseModel):
    moves: list[Move]
    score: int
    