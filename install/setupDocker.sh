#! /bin/bash
sudo apt -y update
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

# start on boot
sudo systemctl enable docker
sudo systemctl daemon-reload 