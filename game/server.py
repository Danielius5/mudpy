import asyncio
import typing

import websockets
import websockets.exceptions

from utils import levenshtein_distance

ServerCommand = typing.Callable[["MudServer", str, str], typing.Awaitable[str]]


# noinspection PyTypeChecker
class MudServer:
    def __init__(self, host, port, greeting_message = None):
        self.host = host
        self.port = port
        self.connected_clients = {}
        self.command_mappings = {}
        self.greeting_message = greeting_message or "Welcome to the MUD!"

    async def validate_user(self, username, password):
        # todo: implement user validation, 
        #  this should access a DB and compare the username and 
        #  the hashed password in the DB
        return username == "test" and password == "test"

    async def handle_client(
            self,
            websocket: websockets.WebSocketServerProtocol,
            path: str,
    ):
        client_name = await websocket.recv()
        client_name = client_name.strip()
        client_password = await websocket.recv()
        client_password = client_password.strip()

        if any([
                not client_name,
                not client_password,
                not await self.validate_user(client_name, client_password),
        ]):
            await websocket.send("Invalid username or password.")
            await websocket.close()
            return
        if client_name in self.connected_clients:
            await websocket.send("You are already connected.")
            await websocket.close()
            return

        self.connected_clients[client_name] = websocket
        print(f"{client_name} connected.")

        try:
            await websocket.send(self.greeting_message)
            while True:
                command = await websocket.recv()
                command = command.strip()
                if not command:
                    continue
                reply = await self.process_command(client_name, command)
                await websocket.send(reply)

        except websockets.exceptions.ConnectionClosed:
            del self.connected_clients[client_name]
            print(f"{client_name} disconnected.")

    async def process_command(
            self,
            sender: str,
            command: str,
    ):
        parts = command.strip().split(maxsplit = 1)

        if parts:
            command_name = parts[0].lower()

            if command_name not in self.command_mappings:
                closest_command = None
                closest_distance = 0.5
                for command in self.command_mappings:
                    distance = await asyncio.get_event_loop().run_in_executor(None, levenshtein_distance, command,
                                                                              command_name)
                    if distance > closest_distance:
                        closest_command = command
                        closest_distance = distance
                if closest_command:
                    # await self.send_to_client(sender, f"Unknown command: {command_name}. Did you mean {closest_command}?")
                    reply = f"Unknown command: {command_name}. Did you mean {closest_command}?"
                else:
                    reply = f"Unknown command: {command_name}."
            else:
                command_args = parts[1] if len(parts) > 1 else ""
                reply = await self.command_mappings.get(command_name)(self, sender, command_args)
            return reply
        else:
            return "Invalid command."

    async def send_to_client(
            self,
            client_name,
            message
    ):
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
        return message


    @server.command("say")
    async def say(server: MudServer, sender: str, args: str):
        args = args.strip()
        if args:
            message = f"{sender} says, \"{args}\""
        else:
            message = f"{sender} says nothing."
        return message


    server.launch()
