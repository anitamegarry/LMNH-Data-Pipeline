#!/bin/bash

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

TABLES=("request_interaction" "rating_interaction")

DB_HOST=${db_host}
DB_PORT=${db_port}
DB_NAME=${db_name}
DB_USER=${db_user}
DB_PASSWORD=${db_password}

export PGPASSWORD=$DB_PASSWORD

reset_interaction_data() {
  for table in "${TABLES[@]}"
  do
    echo "Clearing data from table: $table"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "TRUNCATE TABLE $table RESTART IDENTITY CASCADE;"
    
    if [ $? -eq 0 ]; then
      echo "$table reset successfully."
    else
      echo "Failed to reset $table." >&2
    fi
  done
}

echo "Starting database reset process..."
reset_interaction_data
echo "Database reset complete."

unset PGPASSWORD
