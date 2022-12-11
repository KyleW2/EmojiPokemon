from concurrent import futures
import pokemon_pb2, pokemon_pb2_grpc
import game_constants
import random
import grpc

class Pokemon(pokemon_pb2_grpc.PokemonServicer):
    def __init__(self):
        # A dictionary mapping player names to their emoji
        self.players = {}

        self.captured = []

        self.lock = None

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

        # Insert into players dictionary
        self.players[name.name] = emoji

        # Spawn player on board
        self.spawnPlayer(name.name)
        
        self.printBoard()

        return pokemon_pb2.Emoji(emoji = emoji)
    
    def lock(self, name, context):
        if self.lock == None:
            self.lock = name.name
            return pokemon_pb2.Lock(success = True)
            
        return pokemon_pb2.Lock(success = False)
    
    # Calls itself until a free space is found for player
    def spawnPlayer(self, name):
        i = random.randint(0, game_constants.GRID_SIZE)
        j = random.randint(0, game_constants.GRID_SIZE)

        if self.space_to_players[(i, j)] == []:
            self.space_to_players[(i, j)].append(name)
            self.player_to_space[name] = (i, j)
        else:
            return self.spawnPlayer(name)
    
    def get_neighbors(self, name, context):
        x, y = self.player_to_space[name.name]

        return pokemon_pb2.Neighbors(
            north = self.space_to_players[(x, y - 1)],
            north_east = self.space_to_players[(x + 1, y - 1)],
            east = self.space_to_players[(x + 1, y)],
            south_east = self.space_to_players[(x + 1, y + 1)],
            south = self.space_to_players[(x, y + 1)],
            south_west = self.space_to_players[(x - 1, y + 1)],
            west = self.space_to_players[(x - 1, y)],
            north_west = self.space_to_players[(x - 1, y - 1)]
        )
    
    def move(self, move, context):
        # Remove player from space_to_player
        old_location = self.player_to_space[move.name]
        x, y = self.player_to_space[move.name]
        self.space_to_players[old_location].remove(move.name)

        # Ugh
        if move.direction == "north":
            new_location = (x, y - 1)
        elif move.direction == "north_east":
            new_location = (x + 1, y - 1)
        elif move.direction == "east":
            new_location = (x + 1, y)
        elif move.direction == "south_east":
            new_location = (x + 1, y + 1)
        elif move.direction == "south":
            new_location = (x, y + 1)
        elif move.direction == "south_west":
            new_location = (x - 1, y + 1)
        elif move.direction == "west":
            new_location = (x - 1, y)
        elif move.direction == "north_west":
            new_location = (x - 1, y - 1)

        # Set location to new one if possible
        if new_location[0] < game_constants.GRID_SIZE and new_location[1] < game_constants.GRID_SIZE:
            self.space_to_players[new_location].append(move.name)
            self.player_to_space[move.name] = new_location

            return pokemon_pb2.Result(success = True, captured = move.name in self.captured)

        # Otherwise set to old location
        self.space_to_players[old_location].append(move.name)
        self.player_to_space[move.name] = old_location
        return pokemon_pb2.Result(success = False, captured = move.name in self.captured)

    # Prints board
    def printBoard(self):
        for i in range(0, game_constants.GRID_SIZE):
            for j in range(0, game_constants.GRID_SIZE):
                # If empty print " "
                if self.space_to_players[(i, j)] == []:
                    print("⬛ ", end = "")
                # If occupied print players emoji
                else:
                    print(self.players[self.space_to_players[(i, j)][0]] + " ", end = "")
            print()

def start():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 10))
    pokemon_pb2_grpc.add_PokemonServicer_to_server(Pokemon(), server)
    server.add_insecure_port(f"[::]:{game_constants.PORT}")
    server.start()
    print(f"Listening on port {game_constants.PORT}")
    server.wait_for_termination(10)
