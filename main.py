from game_manager import GameManager


def main():
    GameManager.start()
    from menus.screens import MainScreen
    MainScreen.start(GameManager.screen, GameManager.clock)
    GameManager.quit()
    
if __name__ == '__main__':
    main()