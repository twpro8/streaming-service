#!/usr/bin/env bash

# ------------------------------------------------------------------------
# Creates databases and respective users. These databases location
# and access credentials are defined on the environment variables
# ------------------------------------------------------------------------

set -e

psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" <<-EOSQL
  CREATE USER ${DB_USERS_USER} WITH PASSWORD '${DB_USERS_PASS}';
  CREATE USER ${DB_CATALOG_USER} WITH PASSWORD '${DB_CATALOG_PASS}';

  CREATE DATABASE ${USERS_DB};
  CREATE DATABASE ${CATALOG_DB};

  GRANT ALL PRIVILEGES ON DATABASE ${USERS_DB} TO ${DB_USERS_USER};
  GRANT ALL PRIVILEGES ON DATABASE ${CATALOG_DB} TO ${DB_CATALOG_USER};
EOSQL

# Grant schema access to each user's DB
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" -d "${USERS_DB}" <<-EOSQL
  GRANT ALL ON SCHEMA public TO ${DB_USERS_USER};
EOSQL

psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" -d "${CATALOG_DB}" <<-EOSQL
  GRANT ALL ON SCHEMA public TO ${DB_CATALOG_USER};
EOSQL
