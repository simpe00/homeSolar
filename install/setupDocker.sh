#! /bin/bash
sudo apt -y update
sudo apt install jq -y 
# install docker-compose
LATEST_COMPOSE_VERSION=$(curl -sSL "https://api.github.com/repos/docker/compose/releases/latest" | grep -o -P '(?<="tag_name": ").+(?=")')
# sudo curl -L "https://github.com/docker/compose/releases/download/${LATEST_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
# sudo chmod +x /usr/local/bin/docker-compose
sudo apt install -y python3-pip libffi-dev
sudo pip3 install docker-compose
sudo curl \
    -L "https://raw.githubusercontent.com/docker/compose/${LATEST_COMPOSE_VERSION}/contrib/completion/bash/docker-compose" \
    -o /etc/bash_completion.d/docker-compose
source ~/.bashrc 

# install docker
sudo apt -y install docker.io

sudo groupadd docker
sudo gpasswd -a $USER docker
sudo service docker restart

# move docker from source to target folder
sudo service docker stop

DOCKER_FOLDER_TARGET="/mnt/usb1/docker"
DOCKER_FOLDER_SOURCE="/var/lib/docker/"
DAEMON_FILE="/etc/docker/daemon.json"
DAEMON_TEMP_FILE="/etc/docker/daemon_temp.json"

if ! test -f ${DAEMON_FILE}; then
    sudo jq -n --arg value1 ${DOCKER_FOLDER_TARGET} '{"data-root":$value1}' | sudo tee ${DAEMON_FILE}
else
    sudo cat ${DAEMON_FILE} | sudo jq --arg value1 ${DOCKER_FOLDER_TARGET} '. + {"data-root":$value1}' | sudo tee ${DAEMON_TEMP_FILE}
    yes | sudo mv ${DAEMON_TEMP_FILE} ${DAEMON_FILE}
fi
sudo rsync -aP ${DOCKER_FOLDER_SOURCE} ${DOCKER_FOLDER_TARGET}
sudo rm -r ${DOCKER_FOLDER_SOURCE}

sudo service docker start 

# start on boot
sudo systemctl enable docker
sudo systemctl daemon-reload 