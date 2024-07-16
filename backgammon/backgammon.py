import random
from models.player import Player
import copy
from models.game_state import GameState
from models.move import Move, MoveType
from typing import Self
import netifaces

type Dice = tuple[int, int]


class Backgammon:
    board: list[int]
    bar: dict[Player, int]
    home: dict[Player, int]
    current_turn: Player
    dice: Dice
    moves_left: list[int]
    history: list[GameState]
    score: dict[Player, int]

    def __init__(self) -> None:
        self.new_game()
        self.score = {
            Player.player1: 0,
            Player.player2: 0,
        }
        
    def new_game(self, winner: Player | None = None):
        self.board = self.create_board()
        self.bar = {
            Player.player1: 0,
            Player.player2: 0,
        }  # Captured pieces for each player
        self.home = {
            Player.player1: 0,
            Player.player2: 0,
        }  # Pieces in the home for each player
        self.roll_dice()
        while self.dice[0] == self.dice[1]:
            self.roll_dice()
        if winner is None:
            self.current_turn = (
                Player.player1 if self.dice[0] > self.dice[1] else Player.player2
            )
        else:
            self.current_turn = winner
        self.history = []
    
    def create_board(self) -> None:
        # Initialize board with pieces in starting positions
        board = [0] * 24
        board[0] = 2  # Two black pieces on position 0
        board[5] = -5  # Five white pieces on position 5
        board[7] = -3  # Three white pieces on position 7
        board[11] = 5  # Five black pieces on position 11
        board[12] = -5  # Five white pieces on position 12
        board[16] = 3  # Three black pieces on position 16
        board[18] = 5  # Five black pieces on position 18
        board[23] = -2  # Two white pieces on position 23
        return board

    def create_board_check(self) -> None:
        # Initialize board with pieces in starting positions
        board = [0] * 24
        board[0] = -2  
        board[1] = -2  
        board[2] = -2  
        board[3] = -3  
        board[4] = -3  
        board[5] = -3  
        board[23] = 1 
        return board
    
    @classmethod
    def from_state(cls, state: GameState) -> Self:
        bg = Backgammon()
        bg.set_state(state)
        return bg

    def set_state(self, state: GameState):
        self.board = state.board
        self.bar = state.bar  # Captured pieces for each player
        self.home = state.home  # Pieces in the home for each player
        self.current_turn = state.current_turn
        self.roll_dice(state.dice)
        self.moves_left = state.moves_left
        self.score = state.score
        self.history = state.history

    def get_state(self) -> GameState:
        return GameState(
            board=copy.deepcopy(self.board),
            bar=copy.deepcopy(self.bar),
            home=copy.deepcopy(self.home),
            current_turn=copy.deepcopy(self.current_turn),
            dice=copy.deepcopy(self.dice),
            moves_left=copy.deepcopy(self.moves_left),
            score=copy.deepcopy(self.score),
            history=copy.deepcopy(self.history),
        )

    @classmethod
    def get_piece_type(cls, player: Player):
        return 1 if player == Player.player1 else -1  # 1 for player1, -1 for player2

    def get_player(self, type: int) -> Player:
        return (
            Player.player1 if type > 0 else Player.player2
        )  # 1 for player1, -1 for player2

    def save_state(self) -> None:
        # Return a deep copy of the relevant attributes
        self.history.append(self.get_state())

    def undo(self):
        if len(self.history) > 0:
            state = self.history.pop()
            self.board = state.board
            self.bar = state.bar
            self.home = state.home
            self.current_turn = state.current_turn
            self.dice = state.dice
            self.moves_left = state.moves_left

    def roll_dice(self, dice: Dice | None = None) -> Dice:
        self.dice = (
            (random.randint(1, 6), random.randint(1, 6)) if dice is None else dice
        )
        if self.dice[0] == self.dice[1]:  # Double roll
            self.moves_left = [self.dice[0]] * 4
        else:
            self.moves_left = [self.dice[0], self.dice[1]]
        return self.dice

    def is_valid_move(self, start: int, end: int) -> bool:
        piece_type = self.get_piece_type(self.current_turn)
        board_range = range(24)
        if start not in board_range or end not in board_range:
            return False
        if self.board[start] * piece_type <= 0:
            return False
        if self.board[end] * piece_type < -1:
            return False
        return True

    def make_move(self, start: int, end: int) -> bool:
        move_distance = abs(end - start)
        if not self.is_valid_move(start, end) or move_distance not in self.moves_left:
            return False

        self.save_state()  # Save state before making a move

        piece_type = self.get_piece_type(self.current_turn)
        self.board[start] -= piece_type

        if self.board[end] * piece_type == -1:  # Hit opponent's single piece
            self.board[end] = piece_type
            self.bar[Player.other(self.current_turn)] += 1
        else:
            self.board[end] += piece_type

        self.moves_left.remove(move_distance)
        return True

    def get_start_position(self) -> int:
        return -1 if self.current_turn == Player.player1 else 24

    def can_leave_bar(self, end: int) -> bool:
        piece_type = self.get_piece_type(self.current_turn)
        return self.board[end] * piece_type > -2

    def leave_bar(self, end: int) -> bool:
        if not self.can_leave_bar(end):
            return False

        self.save_state()
        piece_type = self.get_piece_type(self.current_turn)

        self.bar[self.current_turn] -= 1

        if self.board[end] * piece_type == -1:  # Hit opponent's single piece
            self.board[end] = piece_type
            self.bar[Player.other(self.current_turn)] += 1
        else:
            self.board[end] += piece_type

        die = abs(self.get_start_position() - end)
        self.moves_left.remove(die)
        return True

    def get_bar_leaving_positions(self) -> list[int]:
        positions: list[int] = []

        if self.get_captured_pieces() == 0:
            return positions

        start = self.get_start_position()

        for die in self.moves_left:
            target_position = start + die * self.get_piece_type(self.current_turn)
            if target_position not in positions and self.can_leave_bar(target_position):
                positions.append(target_position)

        return positions

    def switch_turn(self) -> Dice:
        self.current_turn = Player.other(self.current_turn)
        self.history = []
        return self.roll_dice()

    def is_bearing_off(self) -> bool:
        home_range = self.get_home_range(self.current_turn)
        piece_type = self.get_piece_type(self.current_turn)
        return not any(
            (pieces * piece_type > 0 and position not in home_range)
            for position, pieces in enumerate(self.board)
        )

    def can_bear_off(self, position: int, die: int) -> bool:
        home_range = self.get_home_range(self.current_turn)
        if not ((position in home_range) and self.is_bearing_off()):
            return False

        piece_type = self.get_piece_type(self.current_turn)
        occupied_positions = [
            position for position in home_range if self.board[position] * piece_type > 0
        ]
        if len(occupied_positions) == 0:
            return False

        die_to_bear_off = (
            24 - position if Player.player1 == self.current_turn else position + 1
        )
        if die_to_bear_off == die:
            return True

        # Allow bearing off from the highest position if the die roll is higher

        farthest_position = (
            max(occupied_positions)
            if self.current_turn == Player.player2
            else min(occupied_positions)
        )

        return (
            position == farthest_position
            and die * piece_type + position not in home_range
        )

    def bear_off(self, position: int) -> bool:

        if not any(self.can_bear_off(position, die) for die in self.moves_left):
            return False

        self.save_state()

        min_die = 24 - position if Player.player1 == self.current_turn else position + 1

        def filter_dice(die):
            return die >= min_die

        higher_dice = filter(filter_dice, self.moves_left)
        die_to_remove = min(higher_dice)
        self.moves_left.remove(die_to_remove)

        self.board[position] -= 1 if self.current_turn == Player.player1 else -1
        self.home[self.current_turn] += 1
        return True

    def is_game_over(self) -> bool:
        return self.get_winner() is not None

    def get_winner(self) -> Player | None:
        if self.home[Player.player2] == 15:
            return Player.player2
        elif self.home[Player.player1] == 15:
            return Player.player1
        return None

    def set_winning_score(self, winner: Player):
        loser = Player.other(player=winner)
        if self.bar[loser] > 0 or any(
            self.board[index] * self.get_piece_type(loser) > 0
            for index in self.get_home_range(winner)
        ):
            self.score[winner] += 3
        elif self.home[loser] > 0:
            self.score[winner] += 1
        else:
            self.score[winner] += 2


    def get_movable_pieces(self) -> list[int]:
        if self.bar[self.current_turn] > 0:
            return []
        placements: list[int] = []
        piece_type = self.get_piece_type(self.current_turn)
        for position, placement in enumerate(self.board):
            if (
                placement * piece_type > 0
                and len(self.get_possible_tracks(position)) > 0
            ):
                placements.append(position)
        return placements

    def is_start_valid(self, start: int):
        return (
            start > -1
            and start < 24
            and self.board[start] * self.get_piece_type(self.current_turn) > 0
        )

    def get_possible_tracks(self, start: int) -> list[int]:
        if not self.is_start_valid(start=start):
            raise ValueError(
                "chosen player is different than the game's turn or start out of bounds"
            )

        possible_tracks: list[int] = []

        piece_type = self.get_piece_type(self.current_turn)
        for die in self.moves_left:
            end = start + die * piece_type
            if (
                self.is_valid_move(start, end) or self.can_bear_off(start, die)
            ) and end not in possible_tracks:
                possible_tracks.append(end)
        return possible_tracks

    def is_turn_done(self) -> bool:
        if len(self.moves_left) == 0:
            return True
        if (
            len(self.get_movable_pieces()) == 0
            and len(self.get_bar_leaving_positions()) == 0
        ):
            return True
        return False

    def get_home_range(self, player: Player) -> range:
        return range(0, 6) if player == Player.player2 else range(18, 24)

    def get_captured_pieces(self) -> int:
        return self.bar[self.current_turn]

    def has_history(self) -> bool:
        return len(self.history) > 0

    def handle_move(self, move: Move):
        match move.move_type:
            case MoveType.normal_move:
                self.make_move(start=move.start, end=move.end)
            case MoveType.bear_off:
                self.bear_off(move.start)
            case MoveType.leave_bar:
                self.leave_bar(move.end)
        

class OnlineBackgammon:
    game: Backgammon
    started: bool
    is_player2_connected: bool
    
    def __init__(self) -> None:
        self.game = Backgammon()
        self.started = False
        self.is_player2_connected = False
        
    def new_game(self):
        if self.game.is_game_over():
            winner = self.game.get_winner()
            self.game.set_winning_score(winner=winner)
        self.game.new_game()