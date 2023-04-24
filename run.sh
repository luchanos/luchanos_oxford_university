#!/bin/bash
export ALEMBIC_DATABASE_URL=postgresql://postgres:postgres@db/postgres # todo luchanos should be explained
sleep 10
alembic upgrade head
