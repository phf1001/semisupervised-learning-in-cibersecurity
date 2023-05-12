#!/bin/bash

docker-compose down -v > /dev/null 2>&1
docker kill $(docker ps -q) > /dev/null 2>&1
docker rmi -f $(docker images -q) > /dev/null 2>&1
docker-compose down -v > /dev/null 2>&1

echo "Iniciando contenedores..."
docker-compose -f docker-compose.yml up -d --build > /dev/null 2>&1

echo "Espere 45 segundos. Estamos asegurando que su base de datos no esté vacía. ¡Así la experiencia será mucho mejor!"
sleep 45

echo "Listo. Inicie 0.0.0.0:5000 en su navegador. ¡Gracias!"
