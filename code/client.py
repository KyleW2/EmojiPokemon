import pokemon_pb2, pokemon_pb2_grpc
import game_constants
import time, signal, grpc
import random

class Client:
    def __init__(self, name: str) -> None:
        self.name = name
        self.lock = False
        self.is_captured = False
        self.path = []
        self.pokedex = []
        self.try_to_capture = False
    
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
        if "pokemon" in self.name:
            print("I've been captured!!!")
        else:
            print(f"I collected {self.pokedex}")

        self.channel.close()
        self.stop()

    def stop(self):
        signal.signal(signal.SIGTERM, interrupt)
    
    def get_neighbors(self):
        response = self.stub.get_neighbors(pokemon_pb2.Name(name = self.name))

        neighbors = {
            "north"      : response.north,
            "east"       : response.east,
            "south"      : response.south,
            "west"       : response.west,
            "north_east" : response.north_east,
            "south_west" : response.south_west,
            "north_west" : response.north_west,
            "south_east" : response.south_east,
        }

        return neighbors
    
    def get_direction(self):
        # Get neighbors
        neighbors = self.get_neighbors()

        # Iterate over space -> players dictionary
        for space, players in neighbors.items():
            for player in players:
                # If we are a pokemon
                if "pokemon" in self.name:
                    if "trainer" in player.name:
                        # Move away from trainers
                        return game_constants.OPPOSITE_DIRECTIONS[space]
                # If we are a trainer
                else:
                    if "pokemon" in player.name:
                        # Set flag to try and capture next step
                        self.try_to_capture = True

                        # Move towards pokemon
                        return space
        
        # If no ones around us :'(
        return game_constants.DIRECTIONS[random.randint(0, 7)]

    def trainer(self):
        # is_captured for trainers will essentially server
        # as a "are there any pokemon" left flag
        while not self.is_captured:
            # Try to get the lock
            self.get_lock()

            # If we have the lock
            if self.lock:
                # If we think were on a pokemon
                if self.try_to_capture:
                    # Capture
                    response = self.stub.capture(pokemon_pb2.Name(name = self.name))

                    # If capture was successful, add pokemon to pokedex
                    if response.emoji != "":
                        self.pokedex.append(response.emoji)
                    
                    self.try_to_capture = False

                # Otherwise, move spaces
                else:
                    # Find direction to move towards pokemon
                    direction = self.get_direction()
                    response = self.stub.move(pokemon_pb2.Move(name = self.name, direction = direction))

                    # Record movement if it went through
                    if response.success:
                        self.path.append(direction)

                    # If captured
                    self.is_captured = response.captured
                    if self.is_captured:
                        self.captured()
                
                # Set the lock to false
                self.lock = False

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

                # Record movement if it went through
                if response.success:
                    self.path.append(direction)

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



    
