## Development Schedule
Week 1
- [x] Assign players a correct emoji
- [x] Spawn players in unique spots
  
Week 2
- [ ] Implment telling players the board
- [ ] Implment players moving
  - [ ] Record player's paths
  
Week 3-4
- [ ] Implment trainers capturing pokemon
  - [ ] Give trainers a pokedex
- [ ] Tell pokemon they're captured
- [ ] Shutdown trainers when all mons are captured

## Emoji Chooser
Each client (either Trainer or Pokemon) will call the server's join method, sending their hostname (trainerN or pokemonN) and recieving a unique emoji back from the server. Once a player joins the game, the server assigns the player a space and updates two hashmaps: player_to_space and space_to_players. The board state is stored in the space_to_players hashmap which maps each possible spot to a list of players currently in that spot.

To configure the size of the grid, number of trainers, and number of pokemon:  
`python3 config.py <N> <T> <P>`  
The script will write a docker-compose file matching the given parameters.

## Protocol Buffer
Currently, the protocol buffer in `code/pokemon.proto` defines join, get_neighbors, move, capture, and captured functions. So far only the join function which allows clients to be assigned an emoji and spawn on the board is implmented. The other functions listed are subject to change as development continues.
