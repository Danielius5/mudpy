from engine import * 
if __name__ == '__main__':
    player = Player(name="Player", short_description="A player.", long_description="A player.", detailed_description="A player.")
    serialized = player.to_json()
    print(serialized)
    deserialized = Player.from_json(serialized)