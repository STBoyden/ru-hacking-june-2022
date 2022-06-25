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

if [[ -z $(which flask 2>/dev/null) ]]; then
  echo "Please install Flask!"
  exit 1
fi

source .env-dev.sh

$container_command run --name currency-comparison-redis-cache \
  -p "$REDIS_PORT:$REDIS_PORT" \
  --rm \
  -d redis:alpine

flask run

$container_command stop -t 1 currency-comparison-redis-cache
