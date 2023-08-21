import asyncio
import typing

import websockets
import websockets.exceptions

from game.system.utils import levenshtein_distance

ClientName = str
ClientMessage = str
ServerResponse = str

CommandArgs = typing.Tuple[str, ...]
ServerCommand = typing.Callable[["MudServer", ClientName, ClientMessage, CommandArgs], ServerResponse]
Clients = typing.Dict[ClientName, websockets.WebSocketServerProtocol]
Commands = typing.Dict[str, ServerCommand]


# noinspection PyTypeChecker
class MudServer:
    def __init__(
            self,
            host: str,
            port: int,
    ):
        self.host = host
        self.port = port
        self.clients: Clients = {}
        self.commands: Commands = {}
        self.loop = asyncio.get_event_loop()

    async def start(self):
        async with websockets.serve(self.handle_client, self.host, self.port):
            self.loop.run_forever()

    async def handle_client(self, client: websockets.WebSocketServerProtocol, path: str):
        client_name = await client.recv()
        self.clients[client_name] = client
        try:
            while True:
                message = await client.recv()
                await client.send(await self.handle_message(client_name, message))
        except websockets.exceptions.ConnectionClosed:
            del self.clients[client_name]

    async def handle_message(self, client_name: ClientName, message: ClientMessage) -> ServerResponse:
        command, *args = message.split(" ")
        if command in self.commands:
            return await self.commands[command](self, client_name, message, args)
        else:
            return f"Command not found. Did you mean: {', '.join(self.get_closest_commands(command))}"

    def get_closest_commands(self, command: str) -> typing.List[str]:
        return sorted(self.commands.keys(), key = lambda c: levenshtein_distance(command, c))[:5]

    def command(self, name: str):
        def wrapper(func: ServerCommand):
            self.commands[name] = func
            return func

        return wrapper

    def send_message(self, client_name: ClientName, message: ServerResponse):
        self.loop.create_task(self.clients[client_name].send(message))

    def broadcast_message(self, message: ServerResponse):
        for client in self.clients.values():
            self.loop.create_task(client.send(message))

    def get_client_names(self) -> typing.List[ClientName]:
        return list(self.clients.keys())

    def get_client(self, client_name: ClientName) -> websockets.WebSocketServerProtocol:
        return self.clients[client_name]
