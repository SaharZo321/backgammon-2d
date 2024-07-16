import select
import socket
import sys
from threading import Thread, Event
from typing import Callable, Any
import pickle
import time
from backgammon.backgammon import OnlineBackgammon, Backgammon
from models.player import Player
from models.move import Move, MoveType
from models.game_state import GameState
from enum import Enum

# from netifaces import interfaces, ifaddresses, AF_INET


# def ip4_addresses() -> list[str]:
#     ip_list = []
#     for interface in interfaces():
#         for link in ifaddresses(interface)[AF_INET]:
#             ip_list.append(link["addr"])
#     return ip_list


def _get_ip_address():
    ip = socket.gethostbyname(socket.gethostname())
    return ip


class ServerFlags(Enum):
    LEAVE = 2
    GET_GAME_STATE = 3
    DONE = 4
    UNDO = 5


class BGServer:

    _event: Event
    _game: OnlineBackgammon
    _server_thread: Thread
    _client_threads: list[Thread]
    _ip: list[str]
    _port: int
    _buffer_size: int
    _starting_time: float

    def _get_game(self) -> Backgammon:
        return self._game.game

    def get_game_state(self) -> GameState:
        return self._game.game.get_state()

    def __init__(self, port: int, buffer_size=2048) -> None:
        self._event = Event()
        self._buffer_size = buffer_size
        self._game = OnlineBackgammon()
        self._client_threads = []

        addresses = [_get_ip_address()]
        print(addresses)
        self._ip = addresses
        self._port = port

        self._server_thread = Thread(target=self._server_setup)

    def start(self) -> None:
        self._server_thread.start()
        self._starting_time = time.time()

    def get_ticks(self):
        return time.time() - self._starting_time

    def _server_setup(self) -> None:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            for ip in self._ip:
                address = (ip, self._port)
                server_socket.bind(address)
        except socket.error as error:
            print(error)

        server_socket.listen(1)
        print("Server has started, waiting for clients")

        while not self._event.is_set():
            readable, writable, errored = select.select([server_socket], [], [], 0.2)
            for r in readable:
                if r is server_socket:
                    connection, address = server_socket.accept()
                    print(address, " has connected to the server")
                    self._check_client_connection_threaded(connection=connection)

        server_socket.close()

    def stop(self) -> None:
        self._event.set()
        print("set")
        for thread in self._client_threads:
            thread.join()
        print("closed client threads: ", len(self._client_threads))
        self._server_thread.join()
        print("closed server thread")
        print("Server stopped")

    def _check_client_connection(self, connection: socket.socket) -> None:
        connection.send(pickle.dumps(self.get_game_state()))
        self._game.is_player2_connected = True
        self._game.started = True
        data = ""
        while not self._event.is_set():
            try:
                raw_data = connection.recv(self._buffer_size)

                if not raw_data:
                    print("Lost connnection to: ", connection.getsockname()[0])
                    self._game.is_player2_connected = False
                    break

                data = pickle.loads(raw_data)
                game = self._get_game()
                if data == ServerFlags.GET_GAME_STATE:
                    pass
                elif data == ServerFlags.UNDO:
                    self.local_undo()
                elif data == ServerFlags.DONE:
                    self.local_done()
                elif data == ServerFlags.LEAVE:
                    print("Player2 left the game.")
                    connection.sendall(pickle.dumps(self.get_game_state()))
                    self._game.is_player2_connected = False
                    break
                else:
                    move: Move = data
                    self.local_move(move)

                print("Recieved: ", data)
                print("Sending current game state")
                connection.sendall(pickle.dumps(self.get_game_state()))

            except socket.error as error:
                print("Disconnected from: ", connection.getsockname())
                print(error)
                break

        self._game.is_player2_connected = False
        connection.close()

    def local_is_alone(self) -> bool:
        return not self._game.is_player2_connected

    def local_has_started(self) -> bool:
        return self._game.started

    def local_is_playing(self) -> bool:
        return self._game.is_player2_connected and self._game.started

    def local_move(self, move: Move) -> GameState:
        game = self._get_game()
        game.handle_move(move=move)
        return self.get_game_state()

    def local_done(self) -> GameState:
        game = self._get_game()
        if not game.is_turn_done():
            return self.get_game_state()
        
        if game.is_game_over():
            self._game.new_game()
        else:
            game.switch_turn()
            
        return self.get_game_state()

    def local_undo(self) -> GameState:
        game = self._get_game()
        game.undo()
        return self.get_game_state()

    def _check_client_connection_threaded(self, connection: socket.socket):
        thread = Thread(
            target=self._check_client_connection,
            args=(connection,),
        )
        self._client_threads.append(thread)
        thread.start()

    def is_alive(self) -> bool:
        return not self._event.is_set()


import math


class Network:
    _client: socket.socket
    _address: tuple[str, int]
    _buffer_size: int
    _id: str
    _tries: int
    _timeout: float
    _event: Event

    connected: bool
    got_last_send: bool
    _time_from_send: float

    def __init__(
        self, ip_address: str, port: int, buffer_size=2048, timeout=5, tries=5
    ) -> None:
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._address = (ip_address, port)
        self._buffer_size = buffer_size
        self.connected = True
        self.got_last_send = False
        self._time_from_send = math.inf
        self._timeout = timeout
        self._tries = tries
        self._client.settimeout(timeout / tries)
        self._event = Event()

    def _connect(
        self, on_connect: Callable[[Any], None], startup_time: float
    ) -> str | None:

        for _ in range(self._tries):
            if self._event.is_set():
                break
            try:
                self._client.connect(self._address)
                self.got_last_send = True
                on_connect(pickle.loads(self._client.recv(self._buffer_size)))
                self._time_from_send = time.time() - startup_time
                break
            except socket.error as error:
                print("Could not establish connection with server... trying again.")
            time.sleep(self._timeout / self._tries)
            self._time_from_send = time.time() - startup_time
        
        self.connected = self.got_last_send

    def connect(self, on_connect: Callable[[Any], None] = lambda data: None):
        self.got_last_send = False
        thread = Thread(
            target=self._connect,
            args=(
                on_connect,
                time.time(),
            ),
        )
        thread.start()
    
    def close(self):
        self._event.set()
        
    def _send(
        self,
        data,
        callback: Callable[
            [
                Any,
            ],
            None,
        ],
        startup_time,
    ) -> None:
        self._client.send(pickle.dumps(data))
        
        for _ in range(self._tries):
            if self._event.is_set():
                break
            try:
                raw_data = self._client.recv(self._buffer_size)
                new_data = pickle.loads(raw_data)
                callback(new_data)
                self.got_last_send = True
                self._time_from_send = time.time() - startup_time

                break
            except socket.error:
                print("Could not connect to the server... trying again.")
            time.sleep(self._timeout / self._tries)
            self._time_from_send = time.time() - startup_time
            
        self.connected = self.got_last_send

    def send(self, data, callback: Callable[[Any], None] = lambda data: None) -> None:
        self.got_last_send = False
        thread = Thread(
            target=self._send,
            args=(
                data,
                callback,
                time.time(),
            ),
        )
        thread.start()

    def is_trying_to_connect(self) -> bool:
        return self._time_from_send > self._timeout / 4