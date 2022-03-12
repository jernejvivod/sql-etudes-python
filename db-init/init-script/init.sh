cd /employees-build-scripts/
psql -U postgres -c "CREATE DATABASE employees"
psql -U postgres -d employees -f employees.sql

