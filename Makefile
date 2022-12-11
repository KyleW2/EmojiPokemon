config:
	python3 config.py $(grid_size) $(trainer_count) $(pokemon_count)
run:
	cd code && docker-compose up --build
pull:
	git pull
	cd code && docker-compose up --build
clean:
	cd code && docker-compose up --remove-orphans