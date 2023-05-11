docker-compose down -v
docker kill $(docker ps -q)
docker rmi -f $(docker images -q)
docker-compose down -v