import asyncio

import websockets


class MudClient:
    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name
        self.websocket = None

    async def connect(self):
        uri = f"ws://{self.host}:{self.port}"
        self.websocket = await websockets.connect(uri)
        await self.websocket.send(self.name)
        print("Connected to server.")

        try:
            while True:
                command = input("Enter a command: ")
                await self.websocket.send(command)
                response = await self.websocket.recv()
                print(response)
                
        except KeyboardInterrupt:
            await self.websocket.close()
            print("Connection closed.")


if __name__ == "__main__":
    name = input("Enter your name: ")
    client = MudClient("localhost", 8765, name)
    asyncio.get_event_loop().run_until_complete(client.connect())
