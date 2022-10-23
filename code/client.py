import pokemon_pb2, pokemon_pb2_grpc
import game_constants
import time, signal, grp

def start(name):
    try:
        with grpc.insecure_channel(f"server:{game_constants.PORT}") as channel:\
            # Get name
            stub = pokemon_pb2_grpc.PokemonStub(channel)
            response = stub.join(pokemon_pb2.Name(name = name))

            print(f"I am {response.emoji}!")

            # Stop
            signal.signal(signal.SIGTERM, gracefull_stop)

    except:
        # Incase server hasn't started yet
        time.sleep(3)
        start(name)


def gracefull_stop():
    raise KeyboardInterrupt()
    
