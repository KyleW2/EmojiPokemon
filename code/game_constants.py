TRAINER_EMOJIS = "😀😁😂😎😍🤩😴🤐🙄😝🤑😤😨🥶🥵😡🤢🤡🤠"
TRAINER_EMOJIS = [emoji for emoji in TRAINER_EMOJIS]

POKEMON_EMOJIS = "🐱🐍🐌🐵🐶🐺🦁🐯🦒🦊🦝🐮🐷🐗🐭🐹🐰🐻🐨🐼🐸🦓🐴🦄🐔🐲🐉🦕🐀🦔🐇🐿🦖🦎🐊🐢🐍🐬🐠🐟"
POKEMON_EMOJIS = [emoji for emoji in POKEMON_EMOJIS]

PORT = 50051

def gracefull_stop():
    raise KeyboardInterrupt()