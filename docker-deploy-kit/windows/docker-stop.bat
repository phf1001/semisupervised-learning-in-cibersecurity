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
echo ~ Liberación de recursos ~
echo.
echo ~ Parando contenedores... ~

docker stop semisupervised-learning-in-cibersecurity_web > nul 2> nul
docker stop semisupervised-learning-in-cibersecurity_db  > nul 2> nul

echo ~ Contenedores parados. ~
