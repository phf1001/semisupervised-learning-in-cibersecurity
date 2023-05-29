:: Author: Patricia Hernando Fernández
@echo off
chcp 65001 > nul 2> nul

echo  _  __ _____   _____  _   _  _____ 
echo ^| ^|/ /^|  __ \ ^|_   _^|^| \ ^| ^|^|_   _^|
echo ^| ' / ^| ^|__) ^|  ^| ^|  ^|  \^| ^|  ^| ^| 
echo ^|  ^<  ^|  _  /   ^| ^|  ^| . ` ^|  ^| ^| 
echo ^| . \ ^| ^| \ \  _^| ^|_ ^| ^|\  ^| _^| ^|_ 
echo ^|_^|\_\^|_^|  \_\^|_____^|^|_^| \_^|^|_____^|
echo.
echo ~ Inicialización por primera vez del sistema ~
echo.
echo ~ Por favor, espera unos instantes mientras se levantan los contenedores. ~
echo ~ Al ser la primera vez, este proceso puede tardar alrededor de un minuto. ~
echo.
docker-compose -f docker-compose.yml up -d --build
echo.
echo ~ Contenedores levantados. ~
echo ~ Por favor, espera 30 segundos mientras se crea la estructura necesaria. ~
timeout /t 30 /NOBREAK > nul
echo.
echo ~ Listo. Por favor, accede a la web introduciendo la siguiente URL en tu navegador: 127.0.0.1:5000/ ~
echo ~ Después, ciérrala y ejecuta el script 'docker-first-time-2.bat'. ~
echo.