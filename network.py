import ipaddress
from queue import Queue, Empty as EmptyQueueError
import socket
from threading import Thread
from typing import Callable, Any
import pickle
import time

import psutil
from backgammon import OnlineBackgammon, Backgammon
from decorators import run_threaded
from models import OnlineGameState, ServerFlags
from models import Move
from pydantic_extra_types.color import Color
import asyncio


class BGServer:
    server: asyncio.Server
    loop: asyncio.AbstractEventLoop

    def __init__(
        self,
        local_color: Color,
        online_color: Color,
        port: int,
        buffer_size=2048,
        timeout: float = 10,
    ) -> None:
        self._ip = self.ip4_addresses()
        self._stop_event = asyncio.Event()
        self._buffer_size = buffer_size
        self.online_backgammon = OnlineBackgammon(
            local_color=local_color, online_color=online_color
        )
        self._timeout = timeout
        self._port = port
        self.connected = False
        self._game_started_event = asyncio.Event()
        self.server_thread: Thread | None = None

    def ip4_addresses(self) -> list[str]:
        ip_list = []
        interfaces = psutil.net_if_addrs()
        for if_name in interfaces:
            interface = interfaces[if_name]
            for s in interface:
                if (
                    s.family == socket.AF_INET
                    and ipaddress.ip_address(s.address).is_private
                ):
                    ip_list.append(s.address)

        return ip_list

    def _get_game(self) -> Backgammon:
        return self.online_backgammon.game

    def local_get_game_state(self) -> OnlineGameState:
        return self.online_backgammon.get_online_game_state()

    async def close_connection(self, writer: asyncio.StreamWriter, address: str):
        print(f"Closing connection to {address}")
        writer.close()
        await writer.wait_closed()

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        address = writer.get_extra_info(name="peername")
        print(f"{address} connected to the server")

        if self.connected:
            print(f"{address} joined to an active game")
            await self.close_connection(writer=writer, address=address)
            return

        self._game_started_event.set()
        self.connected = True

        while not self._stop_event.is_set():
            try:
                raw_data = await asyncio.wait_for(
                    reader.read(self._buffer_size), timeout=self._timeout
                )
                if not raw_data:
                    print(f"Received no data from {address}")
                    break
                request = pickle.loads(raw_data)
                print(f"Received data from {address}: {request}")
                if request == ServerFlags.get_current_state:
                    pass
                elif request == ServerFlags.undo:
                    self.undo_move()
                elif request == ServerFlags.done:
                    self.done_turn()
                elif request == ServerFlags.leave:
                    print(f"Player2 ({address}) left the game.")

                    self.connected = False
                    self.online_backgammon.is_player2_connected = False
                    break
                elif type(request) is Move:
                    manipulated_move: Move = request
                    move = self.online_backgammon.manipulate_move(move=manipulated_move)
                    self.move_piece(move)
                elif type(request) is Color:
                    self.online_backgammon.online_color = request

                response = self.online_backgammon.manipulate_board()
                await self.send_data(writer=writer, data=response)
                print(f"Data sent back to: {address}: {type(response)}")

            except TimeoutError:
                print(f"Lost connection to {address}: waiting for connection")
                self.connected = False
                break
            except asyncio.CancelledError:
                self.connected = False
                print(f"Connection to {address} cancelled")
                break

        await self.close_connection(writer=writer, address=address)

    async def send_data(self, writer: asyncio.StreamWriter, data):
        writer.write(pickle.dumps(data))
        await writer.drain()

    def run_server(self):
        if self.server_thread is not None:
            print("Server already running.")
            return

        if self._stop_event.is_set():
            self._stop_event = asyncio.Event()
            print("Starting again.")

        async def start_server():
            self.server = await asyncio.start_server(
                host=self._ip,
                port=self._port,
                client_connected_cb=self.handle_client,
                limit=self._buffer_size,
            )
            addresses = ", ".join(
                str(sock.getsockname()) for sock in self.server.sockets
            )
            print(f"Serving on {addresses}")

            async with self.server:
                try:
                    await self.server.serve_forever()
                except asyncio.CancelledError:
                    print("Server stopped.")

        @run_threaded(daemon=True)
        def start():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(start_server())

        self.server_thread = start()

    def stop_server(self):
        print("Server shutting down")
        self._stop_event.set()

        async def close_server():
            if self.server:
                self.server.close()
                await self.server.wait_closed()

        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(close_server(), self.loop)

        if self.server_thread is not None:
            self.server_thread.join()
            self.server_thread = None

    @property
    def game_started(self) -> bool:
        return self._game_started_event.is_set()

    def set_local_color(self, local_color: Color) -> None:
        self.online_backgammon.local_color = local_color

    def move_piece(self, move: Move) -> OnlineGameState:
        backgammon = self._get_game()
        backgammon.handle_move(move=move)
        return self.local_get_game_state()

    def done_turn(self) -> OnlineGameState:
        backgammon = self._get_game()
        if not backgammon.is_turn_done():
            return self.local_get_game_state()

        if backgammon.is_game_over():
            self.online_backgammon.new_game()
        else:
            backgammon.switch_turn()

        return self.local_get_game_state()

    def undo_move(self) -> OnlineGameState:
        backgammon = self._get_game()
        backgammon.undo()
        return self.local_get_game_state()

    def is_alive(self) -> bool:
        return self.server.is_serving()


class NetworkClient:
    def __init__(
        self,
        host_ip: str,
        port: int,
        buffer_size=2048,
        timeout: float = 10,
    ) -> None:
        self.host = host_ip
        self.port = port
        self._buffer_size = buffer_size
        self._timeout = timeout
        self._timed_out_event = asyncio.Event()
        self._started_event = asyncio.Event()
        self._stop_event = asyncio.Event()
        self.request_queue: Queue[tuple[Any, Callable[[Any], None]]] = Queue()
        self.time_on_receive = 0
        self.client_thread = None

    async def handle_connection(self):
        try:
            reader, writer = await asyncio.wait_for(
                fut=asyncio.open_connection(host=self.host, port=self.port),
                timeout=self._timeout,
            )
            self._started_event.set()
            print(f"Connected to {self.host}")
        except ConnectionRefusedError:
            print(f"{self.host} refused to connect")
            self._stop_event.set()
            return
        except:
            print(f"Could not establish connection to {self.host}")
            self._stop_event.set()
            return
        # loop to send messages

        while not self._stop_event.is_set():
            try:
                data, on_receive = self.request_queue.get(timeout=1)
                await self.handle_send_data(data=data, writer=writer)
                self.request_queue.task_done()
                await self.handle_received_data(on_receive=on_receive, reader=reader)
            except EmptyQueueError:
                print("Empty queue...")
                continue

        writer.close()
        await writer.wait_closed()
        print("closed writer")

    async def handle_send_data(self, data, writer: asyncio.StreamWriter):
        writer.write(pickle.dumps(data))
        await writer.drain()
        # print(f"Data sent: {data}")

    async def handle_received_data(
        self, on_receive: Callable[[Any], None], reader: asyncio.StreamReader
    ):
        try:
            raw_data = await asyncio.wait_for(
                reader.read(self._buffer_size), timeout=self._timeout
            )
            if not raw_data:
                self.disconnect(threaded=True)
                print("Received no data, closing client")
                return
            # print("Data received.")
            data = pickle.loads(raw_data)
            on_receive(data)
            self.time_on_receive = time.time()
        except TimeoutError:
            self.disconnect(threaded=True)
            print("Timed out... Closing client")
        except Exception as ex:
            self.disconnect(threaded=True)
            print(f"Un handled exception: {ex}")

    def send(self, data, on_receive: Callable[[Any], None] = lambda x: None):
        if not self._started_event.is_set() or self._stop_event.is_set():
            print("Not connected, cannot send")
            return
        request = (data, on_receive)
        self.request_queue.put(request)

    def connect(self):
        if self.client_thread:
            print(f"Already connected to {self.host}.")

        self.request_queue = Queue()
        self._started_event = asyncio.Event()
        self._stop_event = asyncio.Event()

        @run_threaded(daemon=True)
        def connect_threaded():
            asyncio.run(self.handle_connection())
            print("Client disconnected")

        self.client_thread = connect_threaded()

    def disconnect(self, data=None, threaded=False):
        if not self.client_thread:
            print("Cannot disconnect. Client not connected")
            return

        if data is not None:
            self.send(data=data)
            self.request_queue.join()
        self._stop_event.set()
        if not threaded:
            self.client_thread.join()
        print(f"Disconnected from: {self.host}")
        self.client_thread = None

    @property
    def connected(self):
        return bool(self.client_thread)

    @property
    def started(self):
        return self._started_event.is_set()

    @property
    def time_from_last_receive(self):
        return time.time() - self.time_on_receive
