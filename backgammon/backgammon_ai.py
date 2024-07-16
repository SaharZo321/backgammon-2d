from models.game_state import GameState
from models.player import Player
from models.move import Move, MoveType
from models.scored_move import ScoredMoves
from backgammon.backgammon import Backgammon
import copy


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
    def copy_moves(cls, moves: list[Move]) -> list[Move]:
        moves_copy: list[Move] = []
        for move in moves:
            moves_copy.append(
                Move(start=move.start, end=move.end, move_type=move.move_type)
            )
        return moves_copy

    @classmethod
    def get_best_move(cls, game: Backgammon) -> ScoredMoves:

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
                scored_moves = cls.get_best_move(game=game)
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
            scored_moves = cls.get_best_move(game=game)
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
