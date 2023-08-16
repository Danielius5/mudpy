import asyncio

import websockets
import websockets.exceptions


class MudServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connected_clients = {}

    async def handle_client(self, websocket, path):
        client_name = await websocket.recv()
        self.connected_clients[client_name] = websocket
        print(f"{client_name} connected.")

        try:
            while True:
                command = await websocket.recv()
                # if the command is not empty
                if command:
                    await self.process_command(client_name, command)
        except websockets.exceptions.ConnectionClosed:
            del self.connected_clients[client_name]
            print(f"{client_name} disconnected.")

    async def process_command(self, sender, command):
        message = f"{sender}: {command}"
        await self.connected_clients[sender].send(message)

    async def start(self):
        start_server = websockets.serve(self.handle_client, self.host, self.port)
        print("MUD server started.")
        await start_server

        # Keep the server running
        await asyncio.Event().wait()


if __name__ == "__main__":
    server = MudServer("localhost", 8765)
    asyncio.run(server.start())
