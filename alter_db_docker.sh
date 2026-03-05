# using db: openmule_db

# display all relations in this db
# docker compose -f docker-compose-psql.yaml exec db psql -U username -d openmule_db -c "\dt"

# alter bids table
# docker compose -f docker-compose-psql.yaml exec db psql -U username -d openmule_db -c "ALTER TABLE bids ALTER COLUMN amount TYPE FLOAT USING amount::FLOAT;"

# change to string
docker compose -f docker-compose-psql.yaml exec db psql -U username -d openmule_db -c "ALTER TABLE bids ALTER COLUMN amount TYPE VARCHAR USING amount::VARCHAR;"