<p  align="center">
<img  src="https://user-images.githubusercontent.com/99904180/228915777-fcfb115c-37f3-45e6-b5a0-78457d13bba9.png"  width="200"  height="220"  />
</p>

<h1  align="center">
<a  href=""> KRINI </a>
</h1>

> Analizador de **phishing** web basado en la plantilla [argon dashboard](https://www.creative-tim.com/product/argon-dashboard-flask)

<p  align="center">
<img  src="https://user-images.githubusercontent.com/99904180/235093981-34a0f7f2-655b-4508-81ab-923789cba00e.png"/>
</p>

## Quick start: ¡arrancamos en local!

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


## Licensing

  ### ORIGINAL TEMPLATE

- Copyright 2019 - present [Creative Tim](https://www.creative-tim.com/)

- Licensed under [Creative Tim EULA](https://www.creative-tim.com/license)

- [Argon Dashboard Flask](https://www.creative-tim.com/product/argon-dashboard-flask) - Provided by [Creative Tim](https://www.creative-tim.com/) and [AppSeed](https://appseed.us)