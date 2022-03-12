FROM postgres:latest

ENV POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres

COPY ./init-script/init.sh /docker-entrypoint-initdb.d/
