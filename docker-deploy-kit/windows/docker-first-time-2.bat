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
echo ~ Iniciando contenedores. ~
docker-compose -f docker-compose.yml up -d --build
echo ~ Contenedores levantados. ~
echo.
echo ~ Por favor, espera 30 segundos. Estamos asegurando que tu base de datos no está vacía. ¡Así la experiencia será mucho mejor! ~
timeout /t 30 /NOBREAK > nul
echo.
echo ~ Listo. Puedes acceder a la web mediante la dirección 127.0.0.1:5000. ¡Gracias! ~
echo ~ Cuando acabes, puedes:
echo -^> Ejecutar el script docker-stop para parar los contenedores (recomendado si se va a seguir ejecutando una segunda vez).
echo -^> Ejecutar el script docker-start para reiniciarlos.
echo -^> Ejecutar el script docker-clean.sh para eliminar imágenes y contenedores (recomendado si no se quiere volver a ejecutar, se borrarán los modelos creados).
echo 