import config
from config import get_font
from game_manager import GameManager
from graphics.elements import Element
from graphics.graphics_manager import GraphicsManager
from graphics.outline_text import OutlineText
from graphics.styled_elements import StyledBetterButton, StyledButton, StyledTextField
from menus.game_screens import BotGame, LocalClientGame, OfflineGame, OnlineClientGame
from menus.menus import OptionsMenu
from menus.screen import Screen
import pygame
from pygame.time import Clock
import ipaddress
import math

from models import Position

class LostConnection(Screen):

    @classmethod
    def start(cls, screen: pygame.Surface, clock: Clock):
        run = True

        lost_connection = OutlineText(
            text="LOST CONNECTION",
            font=get_font(100),
            text_color=pygame.Color("white"),
            outline_color=pygame.Color("black"),
            position=Position(coords=(config.SCREEN.centerx, 200)),
        )
        
        to_the_server = OutlineText(
            text="TO THE SERVER",
            font=get_font(100),
            text_color=pygame.Color("white"),
            outline_color=pygame.Color("black"),
            position=Position(coords=(config.SCREEN.centerx, 300)),
        )
        

        def back_click():
            nonlocal run
            run = False

        back_button = StyledButton(
            position=Position(coords=(config.SCREEN.centerx, 650)),
            text_input="BACK",
            font=get_font(50),
            on_click=back_click,
        )

        buttons = [back_button]

        while run:
            GraphicsManager.render_background(screen)
            clock.tick(config.FRAMERATE)

            lost_connection.update(screen)
            to_the_server.update(screen)
            
            cls.render_elements(screen=screen, elements=buttons)
            pygame.mouse.set_cursor(cls._get_cursor(elements=buttons))
            
            events = pygame.event.get()
            
            cls.check_quit(events=events, quit=GameManager.quit)
            cls.click_elements(elements=buttons, events=events)

            pygame.display.flip()


class JoinRoomScreen(Screen):

    @classmethod
    def start(cls, screen: pygame.Surface, clock: Clock):
        run = True

        ip_address = GameManager.options.ip

        def back_click():
            nonlocal run
            run = False

        def join_click():
            if not cls._is_valid_ip(ip_address):
                return
            OnlineClientGame.start(screen=screen, clock=clock, ip_address=ip_address)
            GameManager.options.ip = ip_address
            back_click()

        join_button = StyledBetterButton(
            position=Position(coords=(config.SCREEN.centerx, 500)),
            text_input="JOIN",
            font=get_font(70),
            on_click=join_click,
        )

        back_button = StyledButton(
            position=Position(coords=(config.SCREEN.centerx, 650)),
            text_input="BACK",
            font=get_font(50),
            on_click=back_click,
        )
        
        def set_ip(ip: str):
            nonlocal ip_address
            ip_address = ip
        
        ip_field = StyledTextField(
            font=get_font(60),
            position=Position(coords=(config.SCREEN.centerx, 300)),
            width=500,
            default=ip_address,
            on_value_changed=set_ip,
            text_align="center",
            on_enter=join_click
        )

        menu_text = OutlineText(
            text="Enter IP Address",
            font=get_font(80),
            text_color=pygame.Color("white"),
            outline_color=pygame.Color("black"),
            position=Position(coords=(config.SCREEN.centerx, 100)),
        )
        
        elements: list[Element] = [back_button, join_button, ip_field]

        while run:

            clock.tick(config.FRAMERATE)

            join_button.disabled=not cls._is_valid_ip(ip_address)
            
            GraphicsManager.render_background(screen)
            
            menu_text.update(screen)
            
            events = pygame.event.get()
            cls.check_quit(events=events, quit=GameManager.quit)
            
            cls.render_elements(screen=screen, elements=elements, events=events)
            pygame.mouse.set_cursor(cls._get_cursor(elements=elements))
            
            cls.click_elements(elements=elements, events=events)

            pygame.display.flip()
            
    @classmethod
    def _is_valid_ip(cls, address: str):
        try:
            return ipaddress.IPv4Address(address).is_private
        except:
            return False


class OnlineScreen(Screen):

    @classmethod
    def start(cls, screen: pygame.Surface, clock: Clock):
        run = True

        def back_click():
            nonlocal run
            run = False

        def join_room_click():
            JoinRoomScreen.start(screen=screen, clock=clock)
            back_click()

        def create_room_click():
            LocalClientGame.start(screen=screen, clock=clock)
            back_click()

        join_room_button = StyledBetterButton(
            position=Position(coords=(config.SCREEN.centerx, 270)),
            text_input="JOIN ROOM",
            font=get_font(70),
            on_click=join_room_click,
        )

        create_room_button = StyledBetterButton(
            position=Position(coords=(config.SCREEN.centerx, 420)),
            text_input="CREATE ROOM",
            font=get_font(70),
            on_click=create_room_click,
        )

        back_button = StyledButton(
            position=Position(coords=(config.SCREEN.centerx, 650)),
            text_input="BACK",
            font=get_font(50),
            on_click=back_click,
        )

        buttons = [join_room_button, back_button, create_room_button]

        while run:

            clock.tick(config.FRAMERATE)
            screen.fill("black")

            GraphicsManager.render_background(screen)

            events = pygame.event.get()
            
            cls.check_quit(events=events, quit=GameManager.quit)
            
            cls.render_elements(screen=screen, elements=buttons, events=events)
            pygame.mouse.set_cursor(cls._get_cursor(elements=buttons))

            cls.click_elements(elements=buttons, events=events)

            pygame.display.flip()


class PlayScreen(Screen):

    @classmethod
    def start(cls, screen: pygame.Surface, clock: Clock):
        run = True

        def back_button_click():
            nonlocal run
            run = False

        def offline_button_click():
            OfflineGame.start(screen=screen, clock=clock)
            nonlocal run
            run = False

        def bot_button_click():
            BotGame.start(screen=screen, clock=clock)
            nonlocal run
            run = False

        def online_button_click():
            OnlineScreen.start(screen, clock)

        online_button = StyledBetterButton(
            position=Position(coords=(config.SCREEN.centerx, 180)),
            text_input="ON LAN",
            font=get_font(75),
            on_click=online_button_click,
        )

        bot_button = StyledBetterButton(
            position=Position(coords=(config.SCREEN.centerx, 330)),
            text_input="AGAINST BOT",
            font=get_font(75),
            on_click=bot_button_click,
        )

        offline_button = StyledBetterButton(
            position=Position(coords=(config.SCREEN.centerx, 480)),
            text_input="1v1",
            font=get_font(75),
            on_click=offline_button_click,
        )

        back_button = StyledButton(
            position=Position(coords=(config.SCREEN.centerx, 650)),
            text_input="BACK",
            font=get_font(50),
            on_click=back_button_click,
        )

        buttons = [online_button, bot_button, offline_button, back_button]

        while run:
            screen.fill("black")
            GraphicsManager.render_background(screen=screen)
            clock.tick(config.FRAMERATE)

            events = pygame.event.get()
            cls.check_quit(events=events, quit=GameManager.quit)
            cls.render_elements(screen=screen, elements=buttons, events=events)
            pygame.mouse.set_cursor(cls._get_cursor(elements=buttons))

            cls.click_elements(elements=buttons, events=events)

            pygame.display.flip()


class OptionsScreen(Screen):
    
    @classmethod
    def start(cls, screen: pygame.Surface, clock: Clock):
        run = True
        
        def close():
            nonlocal run
            run = False
        
        while run:
            events = pygame.event.get()
            cls.check_quit(events=events, quit=GameManager.quit)
            
            GraphicsManager.render_background(screen=screen)
            clock.tick(config.FRAMERATE)
            OptionsMenu.start(screen=screen, on_top=False, close=close, events=events)
            pygame.display.flip()


class MainScreen(Screen):

    @classmethod
    def start(cls, screen: pygame.Surface, clock: Clock):
        def play_button_click():
            PlayScreen.start(screen=screen, clock=clock)

        def options_button_click():
            OptionsScreen.start(screen=screen, clock=clock)

        def quit_button_click():
            GameManager.quit()

        main_menu = OutlineText(
            text="MAIN MANU",
            font=get_font(100),
            text_color=pygame.Color("white"),
            outline_color=pygame.Color("black"),
            position=Position(coords=(config.SCREEN.centerx, 100)),
        )

        play_button = StyledBetterButton(
            position=Position(coords=(config.SCREEN.centerx, 300)),
            text_input="PLAY",
            font=get_font(75),
            on_click=play_button_click,
        )

        options_button = StyledBetterButton(
            position=Position(coords=(config.SCREEN.centerx, 450)),
            text_input="OPTIONS",
            font=get_font(75),
            on_click=options_button_click,
        )

        quit_button = StyledButton(
            position=Position(coords=(config.SCREEN.centerx, 650)),
            text_input="QUIT",
            font=get_font(50),
            on_click=quit_button_click,
        )

        buttons = [play_button, options_button, quit_button]
        while True:
            clock.tick(config.FRAMERATE)

            screen.fill("black")

            GraphicsManager.render_background(screen=screen)

            main_menu.update(screen)

            events = pygame.event.get()
            cls.check_quit(events=events, quit=GameManager.quit)
            
            cls.render_elements(screen=screen, elements=buttons, events=events)
            pygame.mouse.set_cursor(cls._get_cursor(elements=buttons))

            cls.click_elements(elements=buttons, events=events)
        
            pygame.display.flip()
            