build:
	docker build -t markitdown-fastapi .

run:
	docker run -d -p 8000:8000 --name markitdown-test --env-file .env.prod markitdown-fastapi

stop:
	docker stop markitdown-test && docker rm markitdown-test
