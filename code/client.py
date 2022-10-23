import pokemon_pb2, pokemon_pb2_grpc
import game_constants
import time
import grpc

def start(name):
    try:
        with grpc.insecure_channel(f"server:{game_constants.PORT}") as channel:
            stub = pokemon_pb2_grpc.PokemonStub(channel)
            print("made it")
            response = stub.join(pokemon_pb2.Name(name = name))

            print(f"I am {response.emoji}!")

            game_constants.gracefull_stop()

    except:
        # Incase server hasn't started yet
        time.sleep(3)
        start(name)
