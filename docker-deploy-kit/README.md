## Deploy Krini in local via Docker

You can access the app via the web or deploy our Docker images. Everything is automatic! 🐳 
Mock data will be included in the database to ensure a positive user experience.

🙇‍♀️ An **administrator user (admin/admin)** and a **standard user (user/user)** have been created by default. Feel free to log in or create your own!

> 💡 First download your O.S scripts (OS-all-files.zip) and extract them &nbsp;&middot;&nbsp; [Linux](https://github.com/phf1001/semisupervised-learning-in-cibersecurity/tree/main/docker-deploy-kit/linux) &nbsp;&middot;&nbsp; [Windows](https://github.com/phf1001/semisupervised-learning-in-cibersecurity/tree/main/docker-deploy-kit/windows)

Then, open a terminal in the directory where the scripts are and then execute them in this order. 

<br />

### Linux 🐧

* **⚠️ PLEASE FOLLOW THE SCREEN INSTRUCTIONS SHOWN ON THE SCRIPTS (CLI OUTPUT)**
* **▶️ [Available tutorial on YouTube](https://youtu.be/a9GE0YIv0RQ)**

Open a terminal in the directory containing the scripts. Execute (in this order):
```sh
# Execute this one only the first time you raise the containers or 
# if the data volume has been removed and you want to reset the database
sh docker-first-time-1.sh  
sh docker-first-time-2.sh

# Now the web is up! Access it via the script instructions :)

# If you want to stop the containes to relaunch them later, you can use
sh docker-stop.sh

# And
sh docker-start.sh

# Once you have finished, you can clean your system using
sh docker-clean.sh
```

Pss: if the database port is in use, you can:
```sh
sudo netstat -p -nlp | grep 5432
sudo kill <PID>
```

Pss: a `data` directory will be created to make your database modifications persistant. If you want to delete it or reset the database, just execute:
```sh
sudo rm -R data
```

<br />

### Windows 🪟

* **⚠️ PLEASE FOLLOW THE SCREEN INSTRUCTIONS SHOWN ON THE SCRIPTS (CLI OUTPUT)**
* **▶️ [Available tutorial on YouTube](https://youtu.be/jBPvhbv3Az0)**
* **🐳 Please be sure Docker Daemon is up! You just have to launch Docker Desktop**
* **🚢 Please be sure ports 5000 and 5432 are free (they usually are)**

Reach via the file explorer the directory where you have extracted the files. Execute (in this order):
```sh
# Execute this one only the first time you raise the containers or 
# if the data volume has been removed and you want to reset the database
docker-first-time-1.bat
docker-first-time-2.bat

# Now the web is up! Access it via the script instructions :)

# If you want to stop the containes to relaunch them later, you can use
docker-stop.bat

# And
docker-start.bat

# Once you have finished, you can clean your system using
docker-clean.bat
```

<br />

### Need more help?

You can check our [wiki](https://github.com/phf1001/semisupervised-learning-in-cibersecurity/wiki/), our [video tutorials](https://www.youtube.com/@KRINIPHISHINGSCANNER/playlists) or the official [documentation](https://github.com/phf1001/semisupervised-learning-in-cibersecurity/tree/main/docs).

<br />

### Contact

Feel free to reach me out! 💌

> GitHub [phf1001](https://github.com/phf1001) &nbsp;&middot;&nbsp; LinkedIn [patriciahf](https://www.linkedin.com/in/patriciahf) &nbsp;&middot;&nbsp; Email [phf1001](mailto:phf1001@alu.ubu.es) 

---

<br />

![krini-banner](https://github.com/phf1001/semisupervised-learning-in-cibersecurity/assets/99904180/3c07452e-ebba-467a-b7af-c87b7370f387)