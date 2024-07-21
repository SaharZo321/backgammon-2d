import config
from config import get_font, get_mid_width
from game_manager import GameManager, SettingsKeys
from graphics.elements import BetterButtonElement
from graphics.elements import ButtonElement
from graphics.graphics_manager import GraphicsManager
from graphics.outline_text import OutlineText
from menus.game_screens import BotGame, LocalClientGame, OfflineGame, OnlineClientGame
from menus.menus import OptionsMenu
from menus.screen import Screen
import pygame
from pygame.time import Clock
import ipaddress
import math


class JoinRoomScreen(Screen):

    @classmethod
    def start(cls, screen: pygame.Surface, clock: Clock):
        run = True

        ip_field_active = False

        def deactivate_ip_field(active: bool = False):
            nonlocal ip_field_active
            ip_field_active = active

        ip_address = GameManager.get_setting(SettingsKeys.ip)

        def back_click():
            nonlocal run
            run = False

        def join_click():
            if not cls._is_valid_ip(ip_address):
                return
            
            OnlineClientGame.start(screen=screen, clock=clock, ip_address=ip_address)
            GameManager.set_setting(SettingsKeys.ip, ip_address)
            back_click()

        JOIN_BUTTON = BetterButtonElement(
            position=(math.floor(get_mid_width()), 500),
            text_input="JOIN",
            font=get_font(70),
            text_color=pygame.Color("black"),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            outline_color=pygame.Color("black"),
            on_click=join_click,
        )

        BACK_BUTTON = ButtonElement(
            background_image=None,
            position=(get_mid_width(), 650),
            text_input="BACK",
            font=get_font(50),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            outline_color=pygame.Color("black"),
            outline_size=1,
            on_click=back_click,
        )

        buttons: list[ButtonElement] = [BACK_BUTTON, JOIN_BUTTON]

        while run:

            clock.tick(config.FRAMERATE)

            mouse_position = pygame.mouse.get_pos()

            JOIN_BUTTON.toggle(disabled=not cls._is_valid_ip(ip_address))

            cls._render_menu(screen=screen, buttons=buttons)

            FIELD_BACKGROUND_RECT = cls._render_text_field(
                text=ip_address, screen=screen, active=ip_field_active
            )
            
            for event in pygame.event.get():
                cls._check_quit(event=event, quit=GameManager.quit)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    cls._click_elements(elements=buttons)

                    if FIELD_BACKGROUND_RECT.collidepoint(mouse_position):
                        deactivate_ip_field(True)
                    else:
                        deactivate_ip_field(False)

                if event.type == pygame.KEYDOWN and ip_field_active:
                    ip_address = cls._next_text(
                        event=event,
                        current_text=ip_address,
                        on_escape=deactivate_ip_field,
                        on_enter=join_click,
                    )

            pygame.display.flip()

    @classmethod
    def _render_text_field(cls, text: str, screen: pygame.Surface, active=True):
        TEXT = OutlineText.render(
            text=text,
            font=get_font(80),
            gfcolor=pygame.Color("white"),
            ocolor=pygame.Color("black"),
        )
        TEXT_RECT = TEXT.get_rect(center=(get_mid_width(), 320))

        MIN_STR = "M"

        MIN_FIELD_BACKGROUND_RECT = (
            get_font(80)
            .render(
                MIN_STR,
                True,
                pygame.Color("white"),
            )
            .get_rect(center=(get_mid_width(), 320))
        )

        FIELD_BACKGROUND_RECT = (
            MIN_FIELD_BACKGROUND_RECT if len(text) <= len(MIN_STR) else TEXT_RECT
        )
        colors = {False: pygame.Color("gray"), True: pygame.Color("white")}

        pygame.draw.rect(
            surface=screen,
            color=colors[active],
            rect=FIELD_BACKGROUND_RECT.scale_by(1.1, 1.1),
            border_radius=20,
        )
        screen.blit(TEXT, TEXT_RECT)

        return FIELD_BACKGROUND_RECT

    @classmethod
    def _is_valid_ip(cls, address: str):
        try:
            return ipaddress.IPv4Address(address).is_private
        except:
            return False

    @classmethod
    def _render_menu(
        cls,
        screen: pygame.Surface,
        buttons: list[ButtonElement],
    ):
        screen.fill("black")

        GraphicsManager.render_background(screen)

        MENU_TEXT = OutlineText.render(
            text="Enter IP Address",
            font=get_font(70),
            gfcolor=pygame.Color("white"),
            ocolor=pygame.Color("black"),
        )
        MENU_RECT = MENU_TEXT.get_rect(center=(get_mid_width(), 80))
        screen.blit(MENU_TEXT, MENU_RECT)

        cls._render_elements(screen=screen, elements=buttons)
        pygame.mouse.set_cursor(cls._get_cursor(elements=buttons))


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

        JOIN_ROOM_BUTTON = BetterButtonElement(
            position=(math.floor(get_mid_width()), 270),
            text_input="JOIN ROOM",
            font=get_font(70),
            text_color=pygame.Color("black"),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            outline_color=pygame.Color("black"),
            on_click=join_room_click,
        )

        CREATE_ROOM_BUTTON = BetterButtonElement(
            position=(math.floor(get_mid_width()), 420),
            text_input="CREATE ROOM",
            font=get_font(70),
            text_color=pygame.Color("black"),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            outline_color=pygame.Color("black"),
            on_click=create_room_click,
        )

        BACK_BUTTON = ButtonElement(
            background_image=None,
            position=(get_mid_width(), 650),
            text_input="BACK",
            font=get_font(50),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            outline_color=pygame.Color("black"),
            outline_size=1,
            on_click=back_click,
        )

        buttons: list[ButtonElement] = [JOIN_ROOM_BUTTON, BACK_BUTTON, CREATE_ROOM_BUTTON]

        while run:

            clock.tick(config.FRAMERATE)
            screen.fill("black")

            GraphicsManager.render_background(screen)

            cls._render_elements(screen=screen, elements=buttons)
            pygame.mouse.set_cursor(cls._get_cursor(elements=buttons))

            for event in pygame.event.get():
                cls._check_quit(event=event, quit=GameManager.quit)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    cls._click_elements(elements=buttons)

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

        ONLINE_BUTTON = ButtonElement(
            background_image=None,
            position=(get_mid_width(), 180),
            text_input="PLAY ON LAN",
            font=get_font(75),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            outline_color=pygame.Color("black"),
            outline_size=1,
            on_click=online_button_click,
        )

        BOT_BUTTON = ButtonElement(
            background_image=None,
            position=(get_mid_width(), 330),
            text_input="PLAY AGAINST BOT",
            font=get_font(75),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            outline_color=pygame.Color("black"),
            outline_size=1,
            on_click=bot_button_click,
        )

        OFFLINE_BUTTON = ButtonElement(
            background_image=None,
            position=(get_mid_width(), 480),
            text_input="PLAY 1v1",
            font=get_font(75),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            outline_color=pygame.Color("black"),
            outline_size=1,
            on_click=offline_button_click,
        )

        BACK_BUTTON = ButtonElement(
            background_image=None,
            position=(get_mid_width(), 650),
            text_input="BACK",
            font=get_font(50),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            outline_color=pygame.Color("black"),
            outline_size=1,
            on_click=back_button_click,
        )

        buttons: list[ButtonElement] = [ONLINE_BUTTON, BOT_BUTTON, OFFLINE_BUTTON, BACK_BUTTON]

        while run:
            screen.fill("black")
            GraphicsManager.render_background(screen=screen)
            clock.tick(config.FRAMERATE)

            cls._render_elements(screen=screen, elements=buttons)
            pygame.mouse.set_cursor(cls._get_cursor(elements=buttons))

            for event in pygame.event.get():
                cls._check_quit(event=event, quit=GameManager.quit)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    cls._click_elements(elements=buttons)

            pygame.display.flip()


class OptionsScreen(Screen):
    
    @classmethod
    def start(cls, screen: pygame.Surface, clock: Clock):
        run = True
        
        def close():
            nonlocal run
            run = False
        
        while run:
            GraphicsManager.render_background(screen=screen)
            clock.tick(config.FRAMERATE)
            events = pygame.event.get()
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

        MENU_TEXT = OutlineText.render(
            text="MAIN MANU",
            font=get_font(100),
            gfcolor=pygame.Color("white"),
            ocolor=pygame.Color("black"),
        )
        MENU_RECT = MENU_TEXT.get_rect(center=(get_mid_width(), 100))

        PLAY_BUTTON = BetterButtonElement(
            position=(get_mid_width(), 300),
            text_input="PLAY",
            font=get_font(75),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            on_click=play_button_click,
        )

        OPTIONS_BUTTON = BetterButtonElement(
            position=(get_mid_width(), 450),
            text_input="OPTIONS",
            font=get_font(75),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            on_click=options_button_click,
        )

        QUIT_BUTTON = ButtonElement(
            background_image=None,
            position=(get_mid_width(), 650),
            text_input="QUIT",
            font=get_font(50),
            base_color=config.BUTTON_COLOR,
            hovering_color=config.BUTTON_HOVER_COLOR,
            on_click=quit_button_click,
        )

        buttons: list[ButtonElement] = [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]
        while True:
            clock.tick(config.FRAMERATE)

            screen.fill("black")

            GraphicsManager.render_background(screen=screen)

            screen.blit(MENU_TEXT, MENU_RECT)

            cls._render_elements(screen=screen, elements=buttons)
            pygame.mouse.set_cursor(cls._get_cursor(elements=buttons))

            for event in pygame.event.get():
                cls._check_quit(event=event, quit=GameManager.quit)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    cls._click_elements(elements=buttons)

            pygame.display.flip()


