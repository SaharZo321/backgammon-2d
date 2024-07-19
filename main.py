from game_manager import GameManager
from menus.screens import MainScreen

GameManager.start()
MainScreen.start(GameManager.screen, GameManager.clock)
GameManager.quit()
