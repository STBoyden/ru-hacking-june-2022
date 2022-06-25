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

if [[ "$container_command" == "docker" && $(id -u) != "0" ]]; then
  echo "Please make sure you're running Docker as root!"
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

$container_command build -t currency-comparison --file ./Containerfile

$container_command run --name currency-comparison \
  -p "5000:5000" \ 
  -p "$POSTGRESQL_PORT:$POSTGRESQL_PORT" \
  -p "$REDIS_PORT:$REDIS_PORT" \
  --rm \
  currency-comparison

$container_command stop -t 1 currency-comparison-redis-cache
$container_command stop -t 1 currency-comparison-postgresql-db
