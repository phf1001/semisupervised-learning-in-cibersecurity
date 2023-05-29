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
echo "${Y}~ Lanzador de la web ~${N}"
echo
echo "${Y}~ Levantando contenedores... ~${N}"
docker start semisupervised-learning-in-cibersecurity_db > /dev/null 2>&1
docker start semisupervised-learning-in-cibersecurity_web > /dev/null 2>&1
echo "${Y}~ Contenedores levantados. ~${N}"
