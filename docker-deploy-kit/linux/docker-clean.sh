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
echo "${Y}~ Limpiador de residuos de docker ~${N}"
echo
read -r -p "Este script borra todos los contenedores y todas las imágenes de tu sistema. ¿Estás seguro de que quieres continuar? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY]) 
	echo "${Y}~ Iniciando limpieza... ~${N}"
	docker-compose down -v > /dev/null 2>&1
	docker kill $(docker ps -q) > /dev/null 2>&1
	docker rmi -f $(docker images -q) > /dev/null 2>&1
	docker rm -f $(docker ps -a -q) > /dev/null 2>&1
	echo "${Y}~ Limpieza terminada. ~${N}"
        ;;
    *)
        echo "${Y}~ Parado. ~${N}"
        ;;
esac
