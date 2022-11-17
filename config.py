import sys

TWO = "  "
FOUR = TWO + TWO
TRAINER_EMOJIS = '😀😁😂😎😍🤩😴🤐🙄😝🤑😤😨🥶🥵😡🤢🤡🤠'
POKEMON_EMOJIS = '🐱🐍🐌🐵🐶🐺🦁🐯🦒🦊🦝🐮🐷🐗🐭🐹🐰🐻🐨🐼🐸🦓🐴🦄🐔🐲🐉🦕🐀🦔🐇🐿🦖🦎🐊🐢🐍🐬🐠🐟'

def header():
    return "version: '3.7'\n\nservices:\n"

def server():
    out = TWO + "server:\n" + FOUR + "build: .\n" + FOUR + "hostname: server\n" + FOUR 
    out += "container_name: Server\n" + FOUR + "networks:\n" + FOUR + TWO + "- default\n"
    return out

def trainer(c, i):
    out = TWO + f"client{c}:\n" + FOUR + "build: .\n" + FOUR + f"hostname: trainer{i}\n" + FOUR 
    out += f"container_name: trainer{i}\n" + FOUR + "networks:\n" + FOUR + TWO + "- default\n"
    return out

def pokemon(c, i):
    out = TWO + f"client{c}:\n" + FOUR + "build: .\n" + FOUR + f"hostname: pokemon{i}\n" + FOUR 
    out += f"container_name: pokemon{i}\n" + FOUR + "networks:\n" + FOUR + TWO + "- default\n"
    return out

def network():
    return "networks:\n  default:\n    driver: bridge"

def build_compose(t, p):
    compose = open("code/docker-compose.yml", "w")

    out = header()
    out += server()

    client_count = 0
    for i in range(0, t):
        out += trainer(client_count, i)
        client_count += 1
    
    for i in range(0, p):
        out += pokemon(client_count, i)
        client_count += 1
    
    out += network()

    compose.write(out)
    compose.close()

def build_constants(n, trainer_emojis = TRAINER_EMOJIS, pokemon_emojis = POKEMON_EMOJIS):
    constants = open("code/game_constants.py", "w", encoding = "utf-8")

    out = f"TRAINER_EMOJIS = '{trainer_emojis}'\n"
    out += "TRAINER_EMOJIS = [emoji for emoji in TRAINER_EMOJIS]\n"
    out += f"POKEMON_EMOJIS = '{pokemon_emojis}'\n"
    out += "POKEMON_EMOJIS = [emoji for emoji in POKEMON_EMOJIS]\n\n"
    out += "PORT = 50051\n"
    out += f"GRID_SIZE = {n}"

    constants.write(out)
    constants.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Please provide the grid size, number of trainers, and number of pokemon")
        print("config.py <N> <T> <P>")
        exit()
    
    n = int(sys.argv[1])
    t = int(sys.argv[2])
    p = int(sys.argv[3])

    build_compose(t, p)
    build_constants(n)