import pokemon_pb2, pokemon_pb2_grpc
import game_constants
import time, signal, grpc
import random

class Client:
    def __init__(self, name: str) -> None:
        self.name = name
        self.lock = False
        self.is_captured = False
    
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
            self.join()
    
    def get_lock(self):
        response = self.stub.lock(pokemon_pb2.Name(name = self.name))
        self.lock = response.success
    
    def captured(self):
        self.channel.close()
        self.stop()

    def stop(self):
        signal.signal(signal.SIGTERM, interrupt)
    
    def get_direction(self):
        # Get neighbors
        neighbors = self.stub.get_neighbors(pokemon_pb2.Name(name = self.name))

        # Iterate over space -> players dictionary
        for space, players in vars(neighbors).items():
            for player in players:
                # If we are a pokemon
                if "pokemon" in self.name:
                    if "trainer" in player:
                        # Move away from trainers
                        return game_constants.OPPOSITE_DIRECTION[space]
                # If we are a trainer
                else:
                    if "pokemon" in player:
                        # Move towards pokemon
                        return space
        
        # If no ones around us :'(
        return game_constants.DIRECTIONS[random.randint(0, 7)]

    def trainer(self):
        pass

    def pokemon(self):
        while not self.is_captured:
            # Try to get the lock
            self.get_lock()

            # If we have the lock
            if self.lock:
                # Find direction to move away from trainer
                direction = self.get_direction()
                response = self.stub.move(pokemon_pb2.Move(name = self.name, direction = direction))

                # Set the lock to false
                self.lock = False

                # If captured
                self.is_captured = response.captured
                if self.is_captured:
                    self.captured()

def interrupt():
    raise KeyboardInterrupt()

def start(name):
    client = Client(name)
    client.play()
    client.stop()



    
