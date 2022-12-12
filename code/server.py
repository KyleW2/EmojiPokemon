from concurrent import futures
import pokemon_pb2, pokemon_pb2_grpc
import game_constants
import random
import grpc

class Pokemon(pokemon_pb2_grpc.PokemonServicer):
    def __init__(self):
        # A dictionary mapping player names to their emoji
        self.players = {}

        # Count of pokemon in the game
        self.pokemon_count = 0

        # A list of player names that have been captured
        self.captured = []

        # A string of the player that currently holds the lock
        self.who_has_lock = ""

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
            self.pokemon_count += 1
            emoji = self.available_pokemon.pop()
        else:
            print("stranger danger")
            game_constants.gracefull_stop()

        # Insert into players dictionary
        self.players[name.name] = emoji

        # Spawn player on board
        self.spawn_player(name.name)
        
        self.print_board()

        return pokemon_pb2.Emoji(emoji = emoji)
    
    def lock(self, name, context):
        if self.who_has_lock == "":
            self.who_has_lock = name.name
            print(f"Giving the lock to {name.name}")
            return pokemon_pb2.Lock(success = True)
            
        return pokemon_pb2.Lock(success = False)

    def capture(self, name, context):
        # Make sure they're holding the lock
        if name.name != self.who_has_lock:
            return pokemon_pb2.Emoji(emoji = "")
        
        # Release the lock
        self.who_has_lock = ""

        # Get capturing player's location
        location = self.player_to_space[name.name]

        # If there is a pokemon -> return that mon's emoji
        for player in self.space_to_players[location]:
            if "pokemon" in player:
                # Set that pokemon as captured
                self.captured.append(player)

                # If all pokemon have been captured
                if len(self.captured) == self.pokemon_count:
                    print("All pokemon have been captured! Game over.")
                    # Set all player (just the trainers left) as captured
                    for trainer in self.players.keys():
                        self.captured.append(trainer)

                # Remove mon from grid
                self.space_to_players[self.player_to_space[player]].remove(player)
                return pokemon_pb2.Emoji(emoji = self.players[player])
        
        # Otherwise return empty
        return pokemon_pb2.Emoji(emoji = "")
    
    # Calls itself until a free space is found for player
    def spawn_player(self, name):
        i = random.randint(0, game_constants.GRID_SIZE)
        j = random.randint(0, game_constants.GRID_SIZE)

        if self.space_to_players[(i, j)] == []:
            self.space_to_players[(i, j)].append(name)
            self.player_to_space[name] = (i, j)
        else:
            return self.spawn_player(name)
    
    def get_neighbors(self, name, context):
        x, y = self.player_to_space[name.name]

        return pokemon_pb2.Neighbors(
            north = [pokemon_pb2.Name(name = p) for p in self.space_to_players[(x, y - 1)]] if y - 1 > 0 else [],
            north_east = [pokemon_pb2.Name(name = p) for p in self.space_to_players[(x + 1, y - 1)]] if y - 1 > 0 and x + 1 < game_constants.GRID_SIZE else [],
            east = [pokemon_pb2.Name(name = p) for p in self.space_to_players[(x + 1, y)]] if x + 1 < game_constants.GRID_SIZE else [],
            south_east = [pokemon_pb2.Name(name = p) for p in self.space_to_players[(x + 1, y + 1)]] if x + 1 < game_constants.GRID_SIZE and y + 1 < game_constants.GRID_SIZE else [],
            south = [pokemon_pb2.Name(name = p) for p in self.space_to_players[(x, y + 1)]] if y + 1 < game_constants.GRID_SIZE else [],
            south_west = [pokemon_pb2.Name(name = p) for p in self.space_to_players[(x - 1, y + 1)]] if x - 1 > 0 and y + 1 < game_constants.GRID_SIZE else [],
            west = [pokemon_pb2.Name(name = p) for p in self.space_to_players[(x - 1, y)]] if x - 1 > 0 else [],
            north_west = [pokemon_pb2.Name(name = p) for p in self.space_to_players[(x - 1, y - 1)]] if x - 1 > 0 and y - 1 > 0 else []
        )
    
    def move(self, move, context):
        # Make sure they're holding the lock
        if move.name != self.who_has_lock:
            return pokemon_pb2.Result(success = False, captured = move.name in self.captured)

        # Release the lock
        self.who_has_lock = ""

        # Check if they're captured
        if move.name in self.captured:
            return pokemon_pb2.Result(success = False, captured = True)

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

        print(f"{move.name} wants to move from {old_location} to {new_location}")

        # Set location to new one if possible
        if new_location[0] < game_constants.GRID_SIZE and new_location[0] > 0 and new_location[1] < game_constants.GRID_SIZE and new_location[1] > 0:
            # Make sure trainer isn't already in the spot
            if "trainer" in move.name:
                for player in self.space_to_players[new_location]:
                    if "trainer" in player:
                        # Add trainer back to spot and return false
                        self.space_to_players[old_location].append(move.name)
                        self.player_to_space[move.name] = old_location
                        return pokemon_pb2.Result(success = False, captured = move.name in self.captured)
            
            # If not -> move player
            self.space_to_players[new_location].append(move.name)
            self.player_to_space[move.name] = new_location

            self.print_board()

            return pokemon_pb2.Result(success = True, captured = move.name in self.captured)

        # Otherwise set to old location
        self.space_to_players[old_location].append(move.name)
        self.player_to_space[move.name] = old_location

        return pokemon_pb2.Result(success = False, captured = move.name in self.captured)

    # Prints board
    def print_board(self):
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
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 1))
    pokemon_pb2_grpc.add_PokemonServicer_to_server(Pokemon(), server)
    server.add_insecure_port(f"[::]:{game_constants.PORT}")
    server.start()
    print(f"Listening on port {game_constants.PORT}")
    server.wait_for_termination(10)
