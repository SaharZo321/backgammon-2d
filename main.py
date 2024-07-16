from menus.main_menu import main_menu
from game_manager import GameManager
from menus.games.offline import offline_game

game = GameManager()
# offline_game(game.screen, game.clock)
main_menu(game.screen, game.clock)
game.quit()
