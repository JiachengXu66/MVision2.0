##Ensure quit on error
set -e
##Execute data initialise setup
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/DataLoading/VD_TD_creation.sql
