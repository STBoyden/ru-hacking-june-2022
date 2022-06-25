#!/usr/bin/env bash

set -xe

container_command=""

if [[ ! -z $(which podman 2>/dev/null) ]]; then
  container_command="podman"
elif [[ ! -z $(which docker 2>/dev/null) ]]; then
  container_command="docker"
else
  echo "Please install either Docker or Podman!"
  exit 1
fi

python3 -m pip install -r ./requirements.txt 1>/dev/null

if [[ -z $(which quart 2>/dev/null) ]]; then
  echo "Please install Quart!"
  exit 1
fi

source .env-dev.sh

$container_command run --name currency-comparison-redis-cache \
  -p "$REDIS_PORT:$REDIS_PORT" \
  --rm \
  -d redis:alpine

$container_command run --name currency-comparison-postgresql-db \
  -p "$POSTGRESQL_PORT:$POSTGRESQL_PORT" \
  -e "POSTGRESQL_USER=$POSTGRESQL_USER" \
  -e "POSTGRESQL_PASSWORD=$POSTGRESQL_PASSWORD" \
  --rm \
  -v currency-comparison-postgresql-db:/bitnami/postgresql \
  -d bitnami/postgresql:latest

quart run

$container_command stop -t 1 currency-comparison-redis-cache
$container_command stop -t 1 currency-comparison-postgresql-db
