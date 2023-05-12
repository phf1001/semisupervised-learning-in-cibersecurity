#!/bin/bash

echo "Por favor, espere unos instantes..."
docker-compose -f docker-compose.yml up -d --build > /dev/null 2>&1

echo "Ya falta menos. Espere 30 segundos mientras se crea la estructura necesaria."
sleep 30

echo "Listo. Por favor, abra la siguiente URL en su navegador: 0.0.0.0:5000/"
echo "Después ciérrela y ejecute el script 'docker-init.sh'."
