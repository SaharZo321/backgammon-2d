from game_manager import GameManager
from menus.screens import MainScreen

GameManager.start()
# offline_game(game.screen, game.clock)
MainScreen.start(GameManager.screen, GameManager.clock)
GameManager.quit()
