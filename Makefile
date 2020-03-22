image_name = flasquiz:latest

image:
	docker build -t $(image_name) .

container:
	docker run -d -p 5000:5000 $(image_name)

debug:
	docker run --rm -p 5000:5000 -v "${PWD}:/src" $(image_name)

local_run:
	python app.py
