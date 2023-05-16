#!/bin/bash
# Author: Patricia Hernando Fernández
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
echo "${Y}~ Inicialización por primera vez del sistema (2) ~${N}"
echo
docker-compose down -v > /dev/null 2>&1
docker kill $(docker ps -q) > /dev/null 2>&1
echo "${Y}~ Iniciando contenedores. ~${N}"
docker-compose -f docker-compose.yml up -d --build
echo "${G}~~~ pss: si tienes el puerto 5432 ocupado, pulsa ctrl + c. Después, puedes ejecutar $sudo netstat -p -nlp | grep 5432 seguido de un $sudo kill <PID> para recuperarlo ~~~${N}"
echo 
echo "${Y}~ Contenedores levantados. ~${N}"
echo "${Y}~ Por favor, espera 30 segundos. Estamos asegurando que tu base de datos no está vacía. ¡Así la experiencia será mucho mejor! ~${N}"
sleep 30
echo 
echo "${Y}~ Listo. Busca 0.0.0.0:5000/ (o 127.0.0.1:5000 si no está disponible) en tu navegador. ¡Gracias! ~${N}"
echo "${Y}~ Cuando acabes puedes:"
echo "${R} -> Ejecutar el script docker-stop para parar los contenedores (recomendado si se va a seguir ejecutando una segunda vez."
echo "${R} -> Ejecutar el script docker-start para reiniciarlos."
echo "${R} -> Ejecutar el script docker-clean.sh para eliminar imágenes y contenedores (recomendado si no se quiere volver a ejecutar, se borrarán los modelos creados). ~${N}"
echo 


