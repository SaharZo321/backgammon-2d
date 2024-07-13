import random
from models.player import Player
import copy

type Dice = dict[str, int]

class Backgammon:
    board: list[int]
    bar: dict[Player, int]
    home: dict[Player, int]
    current_turn: Player
    dice: Dice
    moves_left: list[int]
    history: list[dict]
    
    def __init__(self) -> None:
        self.board = self.create_board()
        self.bar = {Player.player1: 0, Player.player2: 0} # Captured pieces for each player
        self.home = {Player.player1: 0, Player.player2: 0}  # Pieces in the home for each player
        self.current_turn = Player.player1
        self.history = []
        self.roll_dice()
        
        
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
        board[5] = -5  # Five white pieces on position 5
        board[7] = -3  # Three white pieces on position 7
        board[20] = 2  # Two white pieces on position 23
        board[21] = 2  # Two white pieces on position 23
        board[22] = 2  # Two white pieces on position 23
        board[23] = 2  # Two white pieces on position 23
        return board
    def get_piece_type(self):
        return 1 if self.current_turn == Player.player1 else -1  # 1 for player1, -1 for player2
    
    
    def get_player(self, type: int) -> Player:
        return Player.player1 if type > 0 else Player.player2  # 1 for player1, -1 for player2
    
    def save_state(self) -> None:
        # Return a deep copy of the relevant attributes
        state = {
            'board': copy.deepcopy(self.board),
            'bar': copy.deepcopy(self.bar),
            'home': copy.deepcopy(self.home),
            'current_turn': self.get_piece_type(),
            'dice': copy.deepcopy(self.dice),
            'moves_left': copy.deepcopy(self.moves_left)
        }
        
        self.history.append(state)
    
    def undo(self):
        if self.history:
            last_state = self.history.pop()
            self.board = last_state['board']
            self.bar = last_state['bar']
            self.home = last_state['home']
            self.current_turn = self.get_player(last_state['current_turn'])
            self.dice = last_state['dice']
            self.moves_left = last_state['moves_left']
    
    def roll_dice(self) -> Dice:
        self.dice = {'die1': random.randint(1, 6), 'die2': random.randint(1, 6)}
        if self.dice['die1'] == self.dice['die2']:  # Double roll
            self.moves_left = [self.dice['die1']] * 4
        else:
            self.moves_left = [self.dice['die1'], self.dice['die2']]
        return self.dice

    def is_valid_move(self, start: int, end: int) -> bool:
        piece_type = self.get_piece_type()
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
        
        self.save_state() # Save state before making a move

        piece_type = self.get_piece_type()
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
    
    def can_leave_bar(self, dice_value: int) -> bool:
        start_position = self.get_start_position()
        piece_type = self.get_piece_type()
        target_position = start_position + dice_value * piece_type
        return self.board[target_position] * piece_type > -2

    def leave_bar(self, dice_value: int) -> bool:
        if not self.can_leave_bar(dice_value):
            return False
        
        self.save_state()
        start_position = self.get_start_position()
        piece_type = self.get_piece_type()
        target_position = start_position + dice_value * piece_type

        self.bar[self.current_turn] -= 1

        if self.board[target_position] * piece_type == -1:  # Hit opponent's single piece
            self.board[target_position] = piece_type
            self.bar[Player.other(self.current_turn)] += 1
        else:
            self.board[target_position] += piece_type

        self.moves_left.remove(dice_value)
        return True
    
    def get_bar_leaving_positions(self) -> list[int]:
        positions: list[int] = []
        
        if not self.get_captured_pieces():
            return positions
        
        start = self.get_start_position()
        
        for die in self.moves_left:
            target_position = start + die * self.get_piece_type()
            if  target_position not in positions and self.can_leave_bar(die):
                positions.append(target_position)
        
        return positions
    
    def switch_turn(self) -> Dice:
        self.current_turn = Player.other(self.current_turn)
        self.history = []
        return self.roll_dice()

    def is_bearing_off(self) -> bool:
        home_range = range(18, 24) if self.current_turn == Player.player1 else range(0, 6)
        piece_type = self.get_piece_type()
        return not any((pieces * piece_type > 0 and position not in home_range) for position, pieces in enumerate(self.board))

    def can_bear_off(self, position: int, die: int) -> bool:
        home_range = range(18, 24) if self.current_turn == Player.player1 else range(0, 6)
        if not ((position in home_range) and self.is_bearing_off()):
            return False
        
        piece_type = self.get_piece_type()
        occupied_positions = [position for position in home_range if self.board[position] * piece_type > 0]
        if len(occupied_positions) == 0:
            return False
        
        die_to_bear_off = 24 - position if Player.player1 == self.current_turn else position + 1
        if die_to_bear_off == die:
            return True
        
        # Allow bearing off from the highest position if the die roll is higher
        
        farthest_position = max(occupied_positions) if self.current_turn == Player.player2 else min(occupied_positions)
        
        # for die in self.moves_left:
        #     if self.current_turn == Player.player1 and lowest_position + die > 23 and lowest_position == position or \
        #         self.current_turn == Player.player2 and highest_position - die and highest_position == position < 0:
        #         return True
        return position == farthest_position and die * piece_type + position not in home_range
               
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
        return all(track >= 0 for track in self.board) or all(track <= 0 for track in self.board)

    def get_winner(self) -> Player | None:
        if all(track >= 0 for track in self.board):
            return Player.player2
        elif all(track <= 0 for track in self.board):
            return Player.player1
        return None
    
    def get_movable_counters(self) -> list[int]:
        if self.bar[self.current_turn] > 0:
            return []
        placements: list[int] = []
        piece_type = self.get_piece_type()
        for position, placement in enumerate(self.board):
            if placement * piece_type > 0 and len(self.get_possible_tracks(position)) > 0:
                placements.append(position)
        return placements
    
    def is_start_valid(self, start: int):
        return (start > -1 and start < 24 and self.board[start] * self.get_piece_type() > 0)
    
    def get_possible_tracks(self, start: int) -> list[int]:
        if not self.is_start_valid(start=start):
            raise ValueError("chosen player is different than the game's turn or start out of bounds")
        
        possible_tracks: list[int] = []
        
        piece_type = self.get_piece_type()
        for die in self.moves_left:
            end = start + die * piece_type
            if (self.is_valid_move(start, end) or self.can_bear_off(start, die)) and end not in possible_tracks:
                possible_tracks.append(end)        
        return possible_tracks
    
    def is_turn_done(self) -> bool:
        if len(self.moves_left) == 0:
            return True
        if len(self.get_movable_counters()) == 0 and len(self.get_bar_leaving_positions()) == 0:
            return True
        return False
    
    def get_captured_pieces(self) -> int:
        return self.bar[self.current_turn]
    
    def has_history(self) -> bool:
        return len(self.history) > 0