#!/bin/bash

sudo -u postgres psql -c "CREATE USER IF NOT EXISTS username WITH PASSWORD 'password';"