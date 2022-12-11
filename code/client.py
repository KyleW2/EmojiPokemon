import pokemon_pb2, pokemon_pb2_grpc
import game_constants
import time, signal, grpc
import random

class Client:
    def __init__(self, name: str) -> None:
        self.name = str
        self.lock = False
        self.stub = None
    
    def play(self) -> None:
        # Join the game
        self.join()

        # Play as the correct type
        if "trainer" in self.name:
            self.trainer()
        elif "pokemon" in self.name:
            self.pokemon()
        else:
            print("😳")
    
    def join(self) -> None:
        try:
            # Try to create the channel and stub
            self.channel = grpc.insecure_channel(f"server:{game_constants.PORT}")
            self.stub = pokemon_pb2_grpc.PokemonStub(self.channel)

            response = self.stub.join(pokemon_pb2.Name(name = self.name))

            print(f"I am {response.emoji}")
        except Exception as e:
            # Incase server hasn't started yet
            time.sleep(1)
            self.join(self.name)
    
    def get_lock(self):
        self.lock = self.stub.lock(pokemon_pb2.Name(name = self.name)).success

    def stop(self):
        self.channel.close()
        raise KeyboardInterrupt()

    def trainer(self):
        if self.lock: 
            print("I got the lock!")
        else:
            print("Who took the lock?!")

    def pokemon(self):
        if self.lock: 
            print("I got the lock!")
        else:
            print("Who took the lock?!")

        """
        response = stub.move(pokemon_pb2.Move(name = name, direction = game_constants.DIRECTIONS[random.randint(0, 7)]))

        print(response.captured)
        while not response.captured:
            response = stub.move(pokemon_pb2.Move(name = name, direction = game_constants.DIRECTIONS[random.randint(0, 7)]))
        """

def start(name):
    client = Client(name)
    client.play()
    client.stop()



    
