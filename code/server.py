from concurrent import futures
import pokemon_pb2, pokemon_pb2_grpc
import game_constants
import random
import grpc

class Pokemon(pokemon_pb2_grpc.PokemonServicer):
    def __init__(self):
        # A dictionary mapping player names to their emoji
        self.players = {}

        self.available_trainers = game_constants.TRAINER_EMOJIS
        self.available_pokemon = game_constants.POKEMON_EMOJIS

        # Shuffle the emoji list so i dont get bored of the same 3 emojis
        random.shuffle(self.available_trainers)
        random.shuffle(self.available_pokemon)

        # To save on look-up time and for general simplicity im using two hashmaps 
        # rather than an NxN matrix
        self.player_to_space = {}
        self.space_to_players = {}
        for i in range(0, game_constants.GRID_SIZE):
            for j in range(0, game_constants.GRID_SIZE):
                self.space_to_players[(i, j)] = []

    def join(self, name, context):
        # Get correct emoji for trainer or pokemon
        if "trainer" in name.name:
            emoji = self.available_trainers.pop()
        elif "pokemon" in name.name:
            emoji = self.available_pokemon.pop()
        else:
            print("stranger danger")
            game_constants.gracefull_stop()

        # Spawn player on board
        print("spawning player")
        self.spawnPlayer(name.name)
        
        print("printing board")
        self.printBoard()

        # Insert into players dictionary
        self.players[name.name] = emoji
        return pokemon_pb2.Emoji(emoji = emoji)
    
    # Calls itself until a free space is found for player
    def spawnPlayer(self, name):
        i = random.randint(0, game_constants.GRID_SIZE)
        j = random.randint(0, game_constants.GRID_SIZE)

        if self.space_to_players[(i, j)] == []:
            self.space_to_players[(i, j)].append(name)
            self.player_to_space[name] = (i, j)
        else:
            return self.spawnPlayer(name)
    
    # Prints board
    def printBoard(self):
        for i in range(0, game_constants.GRID_SIZE):
            for j in range(0, game_constants.GRID_SIZE):
                # If empty print " "
                if self.space_to_players == []:
                    print(" ", end = "")
                # If occupied print players emoji
                else:
                    print(self.players[self.space_to_players[(i, j)]], end = "")
            print()

def start():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 1))
    pokemon_pb2_grpc.add_PokemonServicer_to_server(Pokemon(), server)
    server.add_insecure_port(f"[::]:{game_constants.PORT}")
    server.start()
    print(f"Listening on port {game_constants.PORT}")
    server.wait_for_termination(10)
