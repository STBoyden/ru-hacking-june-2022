#!/usr/bin/env bash


if [[ -z $(which flask) ]]; then
  echo "Please install flask!"
  exit 1
fi

set -xe

source .env-dev.sh
flask run
