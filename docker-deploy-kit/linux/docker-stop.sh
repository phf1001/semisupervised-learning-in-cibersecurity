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
echo "${Y}~ Parar contenedores ~${N}"
echo
echo "${Y}~ Parando contenedores... ~${N}"
docker stop semisupervised-learning-in-cibersecurity_web > /dev/null 2>&1
docker stop semisupervised-learning-in-cibersecurity_db > /dev/null 2>&1
echo "${Y}~ Contenedores parados. ~${N}"