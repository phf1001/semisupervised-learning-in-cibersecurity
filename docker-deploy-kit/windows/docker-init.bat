@echo off
:: Author: Patricia Hernando Fernández
chcp 65001 > nul 2> nul

echo  _  __ _____   _____  _   _  _____ 
echo ^| ^|/ /^|  __ \ ^|_   _^|^| \ ^| ^|^|_   _^|
echo ^| ' / ^| ^|__) ^|  ^| ^|  ^|  \^| ^|  ^| ^| 
echo ^|  ^<  ^|  _  /   ^| ^|  ^| . ` ^|  ^| ^| 
echo ^| . \ ^| ^| \ \  _^| ^|_ ^| ^|\  ^| _^| ^|_ 
echo ^|_^|\_\^|_^|  \_\^|_____^|^|_^| \_^|^|_____^|
echo.
echo ~ Lanzador de la web ~
echo.
docker-compose down -v > nul 2> nul
docker kill $(docker ps -q) > nul 2> nul
docker rm $(docker ps -a -q) > nul 2> nul
docker rmi -f $(docker images -q) > nul 2> nul
echo ~ Iniciando contenedores. ~
docker-compose -f docker-compose.yml up -d --build
echo ~ Contenedores levantados. ~
echo.
echo ~ Por favor, espera 45 segundos. Estamos asegurando que tu base de datos no está vacía. ¡Así la experiencia será mucho mejor! ~
timeout /t 45 /NOBREAK > nul
echo.
echo ~ Listo. Busca 0.0.0.0:5000/ (o 127.0.0.1:5000 si no está disponible) en tu navegador. ¡Gracias! ~
echo ~ Cuando acabes puedes ejecutar el script docker-clean.bat para asegurar que tu ordenador queda limpio. ~
echo.