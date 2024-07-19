import select
import socket
from threading import Thread, Event
from typing import Callable, Any
import pickle
import time
from backgammon import OnlineBackgammon, Backgammon
from models import OnlineGameState
from models import Move
from enum import Enum
import psutil
import ipaddress
from pydantic_extra_types.color import Color


def ip4_addresses() -> list[str]:
    ip_list = []
    interfaces = psutil.net_if_addrs()
    for if_name in interfaces:
        interface = interfaces[if_name]
        for s in interface:
            if s.family == socket.AF_INET and ipaddress.ip_address(s.address).is_private:
                ip_list.append(s.address)
    
    return ip_list


class ServerFlags(Enum):
    LEAVE = 2
    GET_GAME_STATE = 3
    DONE = 4
    UNDO = 5
    
class BGServer:

    _event: Event
    _game: OnlineBackgammon
    _server_thread: Thread
    _server_sockets: list[socket.socket]
    _client_threads: list[Thread]
    _ip: list[str]
    _port: int
    _buffer_size: int
    _starting_time: float

    def _get_game(self) -> Backgammon:
        return self._game.game

    def local_get_game_state(self) -> OnlineGameState:
        return self._game.get_game_state()

    def __init__(self, local_color: Color, online_color: Color, port: int, buffer_size=2048, timeout = 10) -> None:
        self._event = Event()
        self._buffer_size = buffer_size
        self._game = OnlineBackgammon(local_color=local_color, online_color=online_color)
        self._game.local_color = local_color
        self._client_threads = []
        self.running = False
        addresses = ip4_addresses()
        print(ip4_addresses())
        self._ip = addresses
        self._timout = timeout
        self._port = port

        self._server_thread = Thread(target=self._server_setup)

    def start(self) -> None:
        self._server_thread.start()
        self._starting_time = time.time()

    def get_ticks(self):
        return time.time() - self._starting_time

    def _server_setup(self) -> None:
        self._server_sockets: list[socket.socket] = []
        try:
            for ip in self._ip:
                address = (ip, self._port)
                try:
                    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_socket.bind(address)
                    self._server_sockets.append(server_socket)
                    print(address, " was binded")
                    server_socket.listen(1)
                except:
                    print(address, " is not valid")
        except socket.error as error:
            print(error)

        print("Server has started, waiting for clients")

        while not self._event.is_set():
            readable, writable, errored = select.select(self._server_sockets, [], [], 0.2)
            for r in readable:
                if any(thread.is_alive() for thread in self._client_threads):
                    continue
                if r in self._server_sockets:
                    server_socket: socket.socket = r
                    connection, address = server_socket.accept()
                    print(address, " has connected to the server via socket: ", server_socket.getsockname())
                    self._check_client_connection_threaded(connection=connection)

        for s in self._server_sockets:
            s.close()
        

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
        connection.send(pickle.dumps(self._game.manipulate_board()))
        self._game.is_player2_connected = True
        self._game.started = True
        data = ""
        connection.settimeout(self._timout)
        while not self._event.is_set():
            try:
                raw_data = connection.recv(self._buffer_size)

                if not raw_data:  # timout finised and got no reply
                    print("Lost connnection to: ", connection.getsockname()[0])
                    self._game.is_player2_connected = False
                    break

                data = pickle.loads(raw_data)
                if data == ServerFlags.GET_GAME_STATE:
                    pass
                elif data == ServerFlags.UNDO:
                    self.local_undo()
                elif data == ServerFlags.DONE:
                    self.local_done()
                elif data == ServerFlags.LEAVE:
                    print("Player2 left the game.")
                    connection.sendall(pickle.dumps(self._game.manipulate_board()))
                    self._game.is_player2_connected = False
                    break
                elif type(data) is Move:
                    manipulated_move: Move = data
                    move = self._game.manipulate_move(move=manipulated_move)
                    self.local_move(move)
                elif type(data) is Color:
                    self._game.online_color = data

                print("Recieved: ", data)
                print("Sending current game state")
                connection.sendall(pickle.dumps(self._game.manipulate_board()))

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

    def local_move(self, move: Move) -> OnlineGameState:
        game = self._get_game()
        game.handle_move(move=move)
        return self.local_get_game_state()

    def local_done(self) -> OnlineGameState:
        game = self._get_game()
        if not game.is_turn_done():
            return self.local_get_game_state()
        
        if game.is_game_over():
            self._game.new_game()
        else:
            game.switch_turn()
            
        return self.local_get_game_state()

    def local_undo(self) -> OnlineGameState:
        game = self._get_game()
        game.undo()
        return self.local_get_game_state()

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
        self, ip_address: str, port: int, buffer_size=2048, timeout=5, tries=10
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