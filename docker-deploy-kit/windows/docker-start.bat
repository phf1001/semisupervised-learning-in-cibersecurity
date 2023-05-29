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
echo ~ Lanzador de la web ~
echo.
echo ~ Levantando contenedores... ~

docker start semisupervised-learning-in-cibersecurity_db  > nul 2> nul
docker start semisupervised-learning-in-cibersecurity_web > nul 2> nul

echo ~ Contenedores levantados. ~
echo ~ Accede a la web a través de la dirección 127.0.0.1:5000. ¡Gracias! ~
