import random
from threading import Thread
from models import GameState, MoveType, OnlineGameState, ScoredMoves
from models import Player
import copy
from models import Move
from typing import Callable, Self

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
        dice = self.roll_dice()
        if winner is None:
            while dice[0] == dice[1]:
                dice = self.roll_dice()
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
        if (start - end) * piece_type > 0:
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

    def bear_off(self, start: int) -> bool:

        if not any(self.can_bear_off(start, die) for die in self.moves_left):
            return False

        self.save_state()

        min_die = 24 - start if Player.player1 == self.current_turn else start + 1

        def filter_dice(die):
            return die >= min_die

        higher_dice = filter(filter_dice, self.moves_left)
        die_to_remove = min(higher_dice)
        self.moves_left.remove(die_to_remove)

        self.board[start] -= 1 if self.current_turn == Player.player1 else -1
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
            start in range(0, 24)
            and self.board[start] * self.get_piece_type(self.current_turn) > 0
        )

    def get_possible_tracks(self, start: int) -> list[int]:
        if not self.is_start_valid(start=start):
            print(start, " is invalid: ", self.board[start] * self.get_piece_type(self.current_turn))
            return []

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


from pydantic_extra_types.color import Color


class OnlineBackgammon:
    game: Backgammon
    started: bool
    is_player2_connected: bool
    local_color: Color
    online_color: Color

    def __init__(self, online_color: Color, local_color: Color) -> None:
        self.game = Backgammon()
        self.started = False
        self.is_player2_connected = False
        self.online_color = online_color
        self.local_color = local_color

    def new_game(self) -> None:
        if self.game.is_game_over():
            winner = self.game.get_winner()
            self.game.set_winning_score(winner=winner)
        self.game.new_game(winner=winner)

    def manipulate_board(self) -> OnlineGameState:
        board = self.game.board
        new_board = [0] * len(board)

        for index, track in enumerate(board):
            oposite_index = len(board) - index - 1
            new_board[oposite_index] = track * -1

        bar = self.game.bar
        new_bar = {
            Player.player1: bar[Player.player2],
            Player.player2: bar[Player.player1],
        }

        home = self.game.home
        new_home = {
            Player.player1: home[Player.player2],
            Player.player2: home[Player.player1],
        }

        current_turn = self.game.current_turn
        new_current_turn = Player.other(current_turn)

        state = self.game.get_state()
        state.board = new_board
        state.bar = new_bar
        state.home = new_home
        state.current_turn = new_current_turn

        return self.get_game_state(state)

    def manipulate_move(self, move: Move) -> Move:
        board_length = len(self.game.board)
        return Move(
            move_type=move.move_type,
            start=board_length - move.start - 1,
            end=board_length - move.end - 1,
        )

    def get_game_state(self, game_state: GameState | None = None) -> OnlineGameState:
        if game_state is None:
            game_state = self.game.get_state()

        return game_state.to_online(
            online_color=self.online_color,
            local_color=self.local_color,
        )


class BackgammonAI:
    PIECE_SAFETY = 1
    PRIME_BUILDING = 1
    PIECE_MOBILITY = 1
    PIECE_BEARING_OFF = 1
    BAR = 1

    @classmethod
    def _evaluate_game_state(cls, state: GameState):
        score = 0

        # Factor 1: Piece Safety
        score += cls.PIECE_SAFETY * cls._evaluate_piece_safety(state=state)

        # Factor 2: Prime Building
        score += cls.PRIME_BUILDING * cls._evaluate_prime_building(state=state)

        # Factor 3: Mobility
        score += cls.PIECE_MOBILITY * cls._evaluate_mobility(state=state)

        # Factor 4: Bearing Off
        score += cls.PIECE_BEARING_OFF * cls._evaluate_bearing_off(state=state)

        # Factor 5: Opponent's Bar
        score += cls.BAR * cls._evaluate_bar(state=state)

        return score

    @staticmethod
    def _evaluate_piece_safety(state: GameState):
        piece_type = Backgammon.get_piece_type(state.current_turn)

        score = 0
        for pos in range(len(state.board)):
            if state.board[pos] * piece_type == 1:
                score -= 5  # Penalize blots
            elif state.board[pos] * piece_type > 1:
                score += 2  # Reward anchors
        return score

    @staticmethod
    def _evaluate_prime_building(state: GameState):
        score = 0
        current_streak = 0
        piece_type = Backgammon.get_piece_type(state.current_turn)
        for pos in range(24):
            if state.board[pos] * piece_type > 1:
                current_streak += 1
            else:
                if current_streak > 1:
                    score += current_streak * 10  # Reward longer primes
                current_streak = 0
        if current_streak > 1:
            score += current_streak * 10  # Reward primes at the end of the board
        return score

    @staticmethod
    def _evaluate_mobility(state: GameState):
        score = 0
        piece_type = Backgammon.get_piece_type(state.current_turn)
        for pos in range(24):
            if state.board[pos] * piece_type > 0:
                for die in range(1, 7):  # Consider all possible die rolls
                    end_pos = pos + die * piece_type
                    if 0 <= end_pos < 24:
                        if state.board[end_pos] * piece_type >= 0:
                            score += 1  # Reward possible legal moves
        return score

    @staticmethod
    def _evaluate_bearing_off(state: GameState):
        score = 0
        piece_type = Backgammon.get_piece_type(state.current_turn)
        home_range = range(18, 24) if piece_type == 1 else range(0, 6)
        for pos in home_range:
            if state.board[pos] * piece_type > 1:
                score += 30  # Reward closer pieces to bearing off
            if state.board[pos] * piece_type == 1:
                score -= 10
        score += (
            state.home[state.current_turn] * 50
        )  # High reward for borne off pieces
        return score

    @staticmethod
    def _evaluate_bar(state: GameState):
        score = 0
        score += (
            state.bar[Player.other(state.current_turn)] * 20
        ) # Reward for opponent's pieces on the bar
        score -= (
            state.bar[state.current_turn] * 20
        )  # Penalize for bot's pieces on the bar
        return score

    @classmethod
    def _get_all_possible_moves(cls, game: Backgammon):
        movable_pieces = game.get_movable_pieces()
        possible_moves: list[Move] = []

        for start in movable_pieces:
            possible_end_pos = game.get_possible_tracks(start=start)

            def to_move(end: int) -> Move:
                move_type: MoveType = (
                    MoveType.bear_off
                    if end not in range(0, 24)
                    else MoveType.normal_move
                )
                return Move(start=start, end=end, move_type=move_type)

            possible_moves += map(to_move, possible_end_pos)

        return possible_moves

    @classmethod
    def local_get_best_move(cls, game: Backgammon) -> ScoredMoves:

        number_of_moves = len(game.moves_left)

        if number_of_moves == 0:
            return ScoredMoves(
                score=cls._evaluate_game_state(game.get_state()),
                moves=[],
            )

        if game.get_captured_pieces() > 0:  # AI has captured pieces
            best_scored_moves = ScoredMoves(moves=[], score=-1000)
            leaving_bar_pos = game.get_bar_leaving_positions()
            print(leaving_bar_pos)
            print("hi")
            for end in leaving_bar_pos:
                game.leave_bar(end)
                scored_moves = cls.local_get_best_move(game=game)
                if scored_moves.score >= best_scored_moves.score:
                    best_scored_moves = scored_moves
                    best_scored_moves.moves.append(
                        Move(
                            move_type=MoveType.leave_bar,
                            start=game.get_start_position(),
                            end=end,
                        )
                    )
                game.undo()
            return best_scored_moves

        current_possible_moves = cls._get_all_possible_moves(game)
        if len(current_possible_moves) == 0:
            return ScoredMoves(
                score=cls._evaluate_game_state(game.get_state()), moves=[]
            )

        best_scored_moves = ScoredMoves(moves=[], score=-1000)

        for move in current_possible_moves:
            move_type = MoveType.normal_move
            if move.end not in range(0, 24):
                move_type = MoveType.bear_off
                game.bear_off(move.start)
            else:
                game.make_move(move.start, move.end)
            scored_moves = cls.local_get_best_move(game=game)
            if scored_moves.score >= best_scored_moves.score:
                best_scored_moves = scored_moves
                best_scored_moves.moves.append(
                    Move(
                        move_type=move_type,
                        start=move.start,
                        end=move.end,
                    )
                )
            game.undo()

        return best_scored_moves

    @classmethod
    def get_best_move(cls, game: Backgammon, callback: Callable[[ScoredMoves], None] = lambda x: None) -> None:

        game_copy = Backgammon.from_state(game.get_state())

        def get_best_move():
            moves = cls.local_get_best_move(game_copy)
            callback(moves)

        thread = Thread(target=get_best_move)
        thread.start()
