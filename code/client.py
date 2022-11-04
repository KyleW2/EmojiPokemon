import pokemon_pb2, pokemon_pb2_grpc
import game_constants
import time, signal, grpc
import random

def trainer(name, stub):
    pass

def pokemon(name):
    channel = grpc.insecure_channel(f"server:{game_constants.PORT}")
    stub = pokemon_pb2_grpc.PokemonStub(channel)

    response = stub.move(pokemon_pb2.Move(name = name, direction = game_constants.DIRECTIONS[random.randint(0, 7)]))

    while not response.captured:
        response = stub.move(pokemon_pb2.Move(name = name, direction = game_constants.DIRECTIONS[random.randint(0, 7)]))

def start(name):
    # Join the game
    try:
        channel = grpc.insecure_channel(f"server:{game_constants.PORT}")
        stub = pokemon_pb2_grpc.PokemonStub(channel)
        response = stub.join(pokemon_pb2.Name(name = name))

        print(f"I am {response.emoji}!")

    except Exception as e:
        # Incase server hasn't started yet
        time.sleep(3)
        start(name)

    # Begin playing
    if "trainer" in name:
        trainer(name)
    elif "pokemon" in name:
        pokemon(name)
    else:
        print("😳")

    # Stop
    signal.signal(signal.SIGTERM, gracefull_stop)


def gracefull_stop():
    raise KeyboardInterrupt()
    
