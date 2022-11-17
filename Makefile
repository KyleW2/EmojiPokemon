run:
	python3 config.py $(grid_size) $(trainer_count) $(pokemon_count)
	cd code && docker-compose up --build