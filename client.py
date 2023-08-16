import asyncio

import websockets


# this will be moved to seperate project, just tapping it up here to make it easier to keep in line with the server side


class MudClient:
    def __init__(self, host, port, name, password):
        self.host = host
        self.port = port
        self.name = name
        self.password = password
        self.websocket = None

    async def connect(self):
        uri = f"ws://{self.host}:{self.port}"
        self.websocket = await websockets.connect(uri)
        await self.websocket.send(self.name)
        await self.websocket.send(self.password)
        print(await self.websocket.recv())

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
    # we should hide the password input
    import getpass

    name = input("Enter your name: ")
    password = getpass.getpass("Enter your password: ")
    client = MudClient("localhost", 8765, name, password)
    asyncio.get_event_loop().run_until_complete(client.connect())
