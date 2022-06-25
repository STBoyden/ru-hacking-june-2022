FROM python:alpine

RUN sed -i.bak 's/\d\.\d+/edge/g' /etc/apk/repositories
RUN apk update
RUN apk upgrade
RUN apk add libpq-dev musl-dev gcc

WORKDIR /www/app
COPY . .
RUN pip install -r ./requirements.txt

env QUART_ENV=release
env QUART_APP=src/main.py
env REDIS_PORT=6379
env POSTGRESQL_PORT=5432
env POSTGRESQL_DATABASE="currency-comparison"
env POSTGRESQL_USERNAME="postgres"
env POSTGRESQL_PASSWORD=""

EXPOSE 5000
CMD ["quart", "run", "--host=0.0.0.0"]
