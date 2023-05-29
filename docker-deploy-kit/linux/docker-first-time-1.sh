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
echo "${Y}~ Inicialización por primera vez del sistema (1)~ ${N}"
echo

read -r -p "Este script libera los puertos 5432 y 5000 de tu sistema (elimina algún proceso en caso de que estén ocupados), además de contenedores previos de Krini ¿Deseas continuar? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY]) 
	docker-compose down -v > /dev/null 2>&1
	docker kill $(docker ps -q) > /dev/null 2>&1
	docker rm semisupervised-learning-in-cibersecurity_web > /dev/null 2>&1
	docker rm semisupervised-learning-in-cibersecurity_db > /dev/null 2>&1
	sudo kill $(sudo lsof -t -i:5432) > /dev/null 2>&1
	sudo kill $(sudo lsof -t -i:5000) > /dev/null 2>&1
	echo "${Y}~ Por favor, espera unos instantes mientras se levantan los contenedores. ~"
	echo "~ Al ser la primera vez, este proceso puede tardar alrededor de un minuto. ~ ${N}"
	echo 
	docker-compose -f docker-compose.yml up -d --build
	echo 
	echo "${G}~~~ pss: si tienes el puerto 5432 ocupado, pulsa ctrl + c. Después, puedes ejecutar $sudo netstat -p -nlp | grep 5432 seguido de un $sudo kill <PID> para recuperarlo y reinicia el script.~~~"
	echo 
	echo "${Y}~ Contenedores levantados... ¡Ya no queda nada! ~"
	echo "${Y}~ Por favor, espera 30 segundos mientras se crea la estructura necesaria. ~"
	sleep 30
	echo 
	echo "${Y}~ Listo. Por favor, accede a la web introduciendo la siguiente dirección en tu navegador: 127.0.0.1:5000/ ~"
	echo "${Y}~ Después, ciérrala y ejecuta el script "docker-first-time-2.sh". ~${N}"
	echo 
        ;;
    *)
        echo "${Y}~ Parado. ~${N}"
        ;;
esac



