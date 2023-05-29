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
echo ~ Limpiador de residuos de docker ~
echo.
echo ~ Iniciando limpieza... ~

setlocal
:PROMPT
SET /P AREYOUSURE=Este script eliminará tus contenedores e imágenes de Docker. ¿Quieres continuar? (Y/[N])
IF /I "%AREYOUSURE%" NEQ "Y" GOTO END
echo ~ Ejecutando limpieza... ~
docker-compose down -v > nul 2> nul
docker kill $(docker ps -q) > nul 2> nul
docker rm $(docker ps -a -q) > nul 2> nul
docker rmi -f $(docker images -q) > nul 2> nul

:END
endlocal
echo ~ Finalizado. ~