## Deploy the web in Docker

You can access the app via the web or deploy our Docker images. Everything is automatic! 🐳

Mock data will be included in the database so that you can play! An administrator user (admin/admin) and a standard user (user/user) have been created. Feel free to log in or create your own!

> 💡 First download your O.S scripts (OS-all-files.zip) and extract them &nbsp;&middot;&nbsp; [Linux](https://github.com/phf1001/semisupervised-learning-in-cibersecurity/tree/dev/docker-deploy-kit/linux) &nbsp;&middot;&nbsp; [Windows](https://github.com/phf1001/semisupervised-learning-in-cibersecurity/tree/dev/docker-deploy-kit/windows) &nbsp;&middot;&nbsp;

Then, change to the directory where the scripts are and then execute them in this order. 
> Please follow the screen instructions! 

### Linux 🐧
Open a terminal in the directory containing the scripts. Execute (in this order):
```sh
sh docker-first-time-1.sh  # Execute this one only the first time you raise the containers or if the data volume have been removed and you want to reset the database
sh docker-first-time-2.sh

# Now the web is up! Access it via the script instructions :)

# If you want to stop the containes to relaunch them later, you can use
sh docker-stop.sh

#And
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

### Windows 🪟
> **Please be sure Docker Daemon is up! You just have to init Docker Desktop**

Reach via the file explorer the directory where you have extracted the files. Execute (in this order):
```sh
docker-first-time-1.bat # Execute this one only the first time you raise the containers
docker-first-time-2.bat

# Now the web is up! Access it via the script instructions :)

# If you want to stop the containes to relaunch them later, you can use
docker-stop.bat

#And
docker-start.bat

# Once you have finished, you can clean your system using
docker-clean.bat
```


### Need more help?

You can check our [Wiki](https://github.com/phf1001/semisupervised-learning-in-cibersecurity/wiki/), our [video tutorials](https://www.youtube.com/channel/UCirwZk466M5P7xmrM0f5_ng) or the official [documentation](https://github.com/phf1001/semisupervised-learning-in-cibersecurity/tree/main/docs).


### Contact

Feel free to reach me out! 💌

> GitHub [phf1001](https://github.com/phf1001) &nbsp;&middot;&nbsp; LinkedIn [patriciahf](https://www.linkedin.com/in/patriciahf) &nbsp;&middot;&nbsp; Email [phf1001](mailto:phf1001@alu.ubu.es) 