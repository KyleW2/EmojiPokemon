## Development Schedule
- [x] Assign players a correct emoji
- [x] Spawn players in unique spots
- [ ] Implment telling players the board
- [ ] Implment players moving
  - [ ] Record player's paths
- [ ] Implment trainers capturing pokemon
  - [ ] Give trainers a pokedex
- [ ] Tell pokemon they're captured
- [ ] Shutdown trainers when all mons are captured

## Emoji Chooser
Each client (either Trainer or Pokemon) will call the server's join method, sending their hostname (trainerN or pokemonN) and recieving a unique emoji back from the server. Once a player joins the game, the server assigns the player a space and updates two hashmaps: player_to_space and space_to_players. The board state is stored in the space_to_players hashmap which maps each possible spot to a list of players currently in that spot.

To configure the size of the grid, number of trainers, and number of pokemon:  
`python3 config.py <N> <T> <P>`