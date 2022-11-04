import pokemon_pb2, pokemon_pb2_grpc
import game_constants
import time, signal, grpc
import random

def trainer(name, stub):
    pass

def pokemon(name, stub):
    response = stub.move(name = name, direction = game_constants.DIRECTIONS[random.randint(0, 7)])

    while response.success:
        response = stub.move(name = name, direction = game_constants.DIRECTIONS[random.randint(0, 7)])

def start(name):
    try:
        with grpc.insecure_channel(f"server:{game_constants.PORT}") as channel:\
            # Get name
            stub = pokemon_pb2_grpc.PokemonStub(channel)
            response = stub.join(pokemon_pb2.Name(name = name))

            print(f"I am {response.emoji}!")

            # Begin playing
            if "trainer" in name:
                trainer(name, stub)
            elif "pokemon" in name:
                pokemon(name, stub)
            else:
                print("😳")

            # Stop
            signal.signal(signal.SIGTERM, gracefull_stop)

    except:
        # Incase server hasn't started yet
        time.sleep(3)
        start(name)


def gracefull_stop():
    raise KeyboardInterrupt()
    
