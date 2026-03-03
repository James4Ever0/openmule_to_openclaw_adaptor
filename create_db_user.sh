#!/bin/bash
cd /tmp
sudo -u postgres psql -c "CREATE USER username WITH PASSWORD 'password';"
sudo -u postgres psql -c "CREATE DATABASE openmule_db;"