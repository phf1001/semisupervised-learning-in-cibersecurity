#!/bin/bash
R='\033[0;31m'   
G='\033[1;32m'   
Y='\033[1;33m'  
B='\033[1;36m'  
N='\033[0m'    
echo "${B} _  __ _____   _____  _   _  _____ "
echo  '| |/ /|  __ \ |_   _|| \ | ||_   _|'
echo  "| ' / | |__) |  | |  |  \| |  | |  "
echo  '|  <  |  _  /   | |  | . ` |  | | '
echo  '| . \ | | \ \  _| |_ | |\  | _| |_ '
echo  "|_|\_\|_|  \_\|_____||_| \_||_____|${N}"
echo
echo "${Y}~ Lanzador de la web ~${N}"
echo
docker-compose down -v > /dev/null 2>&1
docker kill $(docker ps -q) > /dev/null 2>&1
docker rmi -f $(docker images -q) > /dev/null 2>&1
docker-compose down -v > /dev/null 2>&1
echo "${Y}~ Iniciando contenedores. ~${N}"
docker-compose -f docker-compose.yml up -d --build
echo "${G}~~~ pss: si tienes el puerto 5432 ocupado, pulsa ctrl + c. Después, puedes ejecutar $sudo netstat -p -nlp | grep 5432 seguido de un $sudo kill <PID> para recuperarlo ~~~${N}"
echo 
echo "${Y}~ Contenedores levantados. ~${N}"
echo "${Y}~ Por favor, espera 45 segundos. Estamos asegurando que tu base de datos no está vacía. ¡Así la experiencia será mucho mejor! ~${N}"
sleep 45
echo 
echo "${Y}~ Listo. Busca 0.0.0.0:5000/ (o 127.0.0.1:5000 si no está disponible) en tu navegador. ¡Gracias! ~${N}"
echo "${Y}~ Cuando acabes puedes ejecutar el script docker-clean.sh para asegurar que tu ordenador queda limpio. ~${N}"
echo 


