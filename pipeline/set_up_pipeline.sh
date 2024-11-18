#!/bin/bash

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

DB_HOST=${db_host}
DB_PORT=${db_port}
DB_NAME=${db_name}
DB_USER=${db_user}
DB_PASSWORD=${db_password}

activate_venv() {
    python3 -m venv .venv
    source ./.venv/bin/activate
}

activate() {
    if [[ $1 == "new" ]]; then
        echo "Recreating virtual environment..."
        deactivate
        rm -rf .venv
        activate_venv
    elif [ -d ".venv" ]; then
        echo "Activating existing virtual environment..."
        source ./.venv/bin/activate
    else
        echo "Creating and activating virtual environment..."
        activate_venv
    fi
}

activate

echo "Installing required Python packages..."
pip3 install -r requirements.txt

echo "Setting up the PostgreSQL database..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f schema.sql

echo "Data pipeline setup complete!"
