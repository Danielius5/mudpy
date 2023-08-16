import asyncio
import typing

import websockets
import websockets.exceptions

from utils import levenshtein_distance

ServerCommand = typing.Callable[["MudServer", str, str], typing.Awaitable[None]]


# noinspection PyTypeChecker
class MudServer:
    def __init__(self, host, port, greeting_message = None):
        self.host = host
        self.port = port
        self.connected_clients = {}
        self.command_mappings = {}
        self.greeting_message = greeting_message or "Welcome to the MUD!"

    async def handle_client(self, websocket, path):
        client_name = await websocket.recv()
        self.connected_clients[client_name] = websocket
        print(f"{client_name} connected.")

        try:
            await websocket.send(self.greeting_message)
            while True:
                command = await websocket.recv()
                await self.process_command(client_name, command)
        except websockets.exceptions.ConnectionClosed:
            del self.connected_clients[client_name]
            print(f"{client_name} disconnected.")

    async def process_command(self, sender, command):
        parts = command.strip().split(maxsplit = 1)

        async def handle_default(server, sender, args):
            return server.send_to_client(sender, f"Unknown command: {command}")

        if parts:
            command_name = parts[0].lower()

            # use lev distance to find the closest command
            if command_name not in self.command_mappings:
                closest_command = None
                closest_distance = 0
                for command in self.command_mappings:
                    distance = levenshtein_distance(command, command_name)
                    if distance > closest_distance:
                        closest_command = command
                        closest_distance = distance
                if closest_command:
                    return await self.send_to_client(sender,
                                                     f"Unknown command: {command}. Did you mean {closest_command}?")

            command_args = parts[1] if len(parts) > 1 else ""
            command_handler = self.command_mappings.get(command_name, handle_default)
            await command_handler(self, sender, command_args)

    async def send_to_client(self, client_name, message):
        if client_name in self.connected_clients:
            client = self.connected_clients[client_name]
            await client.send(message)

    async def send_to_all_clients(self, message):
        for client in self.connected_clients.values():
            await client.send(message)

    async def start_websocket(self):
        start_server = websockets.serve(self.handle_client, self.host, self.port)
        print("MUD server started.")
        await start_server

        await asyncio.Event().wait()

    def launch(self):
        asyncio.run(server.start_websocket())

    def register_new_command(self, command, callback: ServerCommand):
        self.command_mappings[command] = callback
        return self

    def command(self, command) -> typing.Callable[[ServerCommand], ServerCommand]:
        def decorator(callback: ServerCommand) -> ServerCommand:
            self.register_new_command(command, callback)
            return callback

        return decorator


if __name__ == "__main__":
    server = MudServer("localhost", 8765)


    @server.command("inspect")
    async def inspect(server: MudServer, sender: str, args: str):
        args = args.strip()
        if args:
            message = f"{sender} inspects {args}."
        else:
            message = f"{sender} inspects nothing."
        asyncio.create_task(server.send_to_client(sender, message))


    @server.command("say")
    async def say(server: MudServer, sender: str, args: str):
        args = args.strip()
        if args:
            message = f"{sender} says, \"{args}\""
        else:
            message = f"{sender} says nothing."
        asyncio.create_task(server.send_to_all_clients(message))


    server.launch()
