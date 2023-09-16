<p align="center">
  <img src="https://user-images.githubusercontent.com/99904180/228915777-fcfb115c-37f3-45e6-b5a0-78457d13bba9.png" width="200" height="220" />
</p>

<h1 align="center">
  <br>
  <a href="https://krini.herokuapp.com/index"> KRINI PHISHING SCANNER </a>
</h1>

<h3 align="center">Analizador web de phishing</h3>

<p align="center" style="font-weight: bold; font-size: 17px">
  📚
  <a href="https://github.com/phf1001/semisupervised-learning-in-cibersecurity/wiki">GitHub Wiki</a> •
  <a href="https://youtube.com/@KRINIPHISHINGSCANNER/playlists">YouTube Channel</a>
  🎥
  <br /><br />
</p>

<p  align="center">
<img  width=70% src="https://user-images.githubusercontent.com/99904180/235093981-34a0f7f2-655b-4508-81ab-923789cba00e.png"/>
</p>

<br  />

## Despliegue en local mediante Docker

🐳 Consulta toda la información necesaria en el [docker-deploy-kit README.md](https://github.com/phf1001/semisupervised-learning-in-cibersecurity/tree/main/docker-deploy-kit) 

<br  />

## Despliegue en local mediante el servidor de Flask

**👩‍💻 ¿Eres programador?** Consulta nuestra [guía del desarrollador](https://github.com/phf1001/semisupervised-learning-in-cibersecurity/wiki/Manual-del-programador) para toda la información relacionada con desarrollo y despliegue.
```bash

# Estando en el repositorio -> Instalación del entorno virtual

# (Unix/Mac)

virtualenv  env
source  env/bin/activate
pip3  install  -r  requirements.txt

# (Windows)

virtualenv env
.\env\Scripts\activate
pip3  install  -r  requirements.txt

# Establecemos la variable de entorno FLASK_APP

(Unix/Mac) export FLASK_APP=run.py
(Windows) set FLASK_APP=run.py
(Powershell) $env:FLASK_APP = ".\run.py"

# Establecemos el modo "Debug"

# (Unix/Mac) export FLASK_ENV=development
# (Windows) set FLASK_ENV=development
# (Powershell) $env:FLASK_ENV = "development"

# Iniciamos la aplicación (modo desarrollo)

# --host=0.0.0.0 - exponer la aplicación en todas las interfaces de red(default 127.0.0.1)
# --port=5000 
flask  run  --host=0.0.0.0  --port=5000

# Acceso en el navegador mediante http://<host>:<port>
```
<br  />


## Licencias

Producto basado en la plantilla [argon dashboard](https://www.creative-tim.com/product/argon-dashboard-flask)

- Copyright 2019 - present [Creative Tim](https://www.creative-tim.com/)

- Licensed under [Creative Tim EULA](https://www.creative-tim.com/license)

- [Argon Dashboard Flask](https://www.creative-tim.com/product/argon-dashboard-flask) - Provided by [Creative Tim](https://www.creative-tim.com/) and [AppSeed](https://appseed.us)


---

<br />

## Information

ℹ Developed in colaboration with the Computer Sciences department of the [University of Burgos](https://www.ubu.es/grado-en-ingenieria-informatica).

<p align="center">
  <img width="25%" height="25%" src="https://github.com/phf1001/semisupervised-learning-in-cibersecurity/assets/99904180/380cadcd-23f0-48e5-a4f4-6be8e4a50f1d"> &nbsp; &nbsp; &nbsp;
  <img width="18%" height="18%" src="https://github.com/phf1001/semisupervised-learning-in-cibersecurity/assets/99904180/19e838c2-34ff-4525-8cd5-7eec205a06f0"> &nbsp; &nbsp; &nbsp;
  <img width="18%" height="18%" src="https://github.com/phf1001/semisupervised-learning-in-cibersecurity/assets/99904180/d6b3918f-4a7b-44ad-9a9b-b83d50c6d650"> &nbsp; &nbsp; &nbsp;
  <img width="8%" height="8%" src="https://github.com/phf1001/semisupervised-learning-in-cibersecurity/assets/99904180/401a9df0-a937-4641-bf4b-908a2d1a708b"> &nbsp; &nbsp; &nbsp;
</p>

---

<br />

![krini-banner](https://github.com/phf1001/semisupervised-learning-in-cibersecurity/assets/99904180/3c07452e-ebba-467a-b7af-c87b7370f387)