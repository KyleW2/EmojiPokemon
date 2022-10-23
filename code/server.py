from concurrent import futures
import pokemon_pb2, pokemon_pb2_grpc
import game_constants
import random
import grpc

class Pokemon(pokemon_pb2_grpc.PokemonServicer):
    def __init__(self):
        # A dictionary mapping player names to their emoji
        self.players = {}

        # Shuffle the emoji list so i dont get bored of the same 3 emojis
        self.available_trainers = random.shuffle(game_constants.TRAINER_EMOJIS)
        self.available_pokemon = random.shuffle(game_constants.POKEMON_EMOJIS)

        print(self.available_pokemon)

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
        print(self.players)
        return pokemon_pb2.Emoji(emoji = emoji)

def start():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 1))
    pokemon_pb2_grpc.add_PokemonServicer_to_server(Pokemon(), server)
    server.add_insecure_port(f"[::]:{game_constants.PORT}")
    server.start()
    print(f"Listening on port {game_constants.PORT}")
    server.wait_for_termination(10)
