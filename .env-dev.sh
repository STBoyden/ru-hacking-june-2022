# General Flask Config
export QUART_APP=src/main.py
export QUART_ENV=development

# Redis Config
export REDIS_HOST="localhost"
export REDIS_PORT=6379

# Postgres Config
export POSTGRESQL_HOST="localhost"
export POSTGRESQL_PORT=5432
export POSTGRESQL_DATABASE="currency-comparison"
export POSTGRESQL_USERNAME="postgres"
[[ -f "./.postgres-password.sh" ]] && source ./.postgres-password.sh
