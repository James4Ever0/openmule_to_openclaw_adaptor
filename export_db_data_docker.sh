DATE_SLUG=$(date +%Y%m%d_%H%M%S)
mkdir -p db_backup
docker compose -f docker-compose-psql.yaml exec db pg_dump -U username openmule_db > db_backup/backup_${DATE_SLUG}.sql
echo "Saved to db_backup/backup_${DATE_SLUG}.sql"