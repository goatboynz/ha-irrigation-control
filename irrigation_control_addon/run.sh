#!/usr/bin/with-contenv bashio

bashio::log.info "Irrigation Control Addon: Initializing..."

# Ensure /data directory exists
if [ ! -d /data ]; then
    bashio::log.info "Creating /data directory structure"
    mkdir -p /data/db
fi

# Get the configured log level
CONFIG_LOG_LEVEL=$(bashio::config 'log_level')
export LOG_LEVEL="${CONFIG_LOG_LEVEL:-info}"

bashio::log.info "Starting Irrigation Control with log level: ${LOG_LEVEL}"

# Initialize the database schema
python /usr/src/app/database_setup.py

# Start the FastAPI application with Uvicorn
cd /usr/src/app || exit 1
exec python -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level "${LOG_LEVEL}"
