#! /bin/bash
sudo apt -y update
sudo apt -y install python3-pip

sudo pip3 install docker-compose
sudo apt -y install docker.io

sudo groupadd docker
sudo gpasswd -a $USER docker
sudo service docker restart

# start on boot
sudo systemctl enable docker

echo "reboot now - and try if docker is running with ´docker ps´"