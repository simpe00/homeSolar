#!/bin/bash
sudo sed -i '$ s/$/ cgroup_enable=cpuset cgroup_enable=memory cgroup_memory=1 swapaccount=1/' /boot/firmware/cmdline.txt

sudo apt-get update && sudo apt-get install -y apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl

sudo apt-mark hold kubectl


MACHINE_TYPE=$(uname -m)
# ARM - Binary download
if [ "${MACHINE_TYPE}" = "aarch64" ]; then
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-arm64
    sudo install minikube-linux-arm64 /usr/local/bin/minikube
    # rm minikube-linux-arm64  
fi

# X86 - Binary download
if [ "${MACHINE_TYPE}" = "x86_64" ]; then
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    sudo install minikube-linux-amd64 /usr/local/bin/minikube
    # rm minikube-linux-amd64
fi

sudo apt-get install -y conntrack # issue from https://github.com/manusa/actions-setup-minikube/issues/33

echo "minikube for ${MACHINE_TYPE} was installed"

if [ "${MACHINE_TYPE}" = "aarch64" ]; then
    curl -L https://github.com/kubernetes/kompose/releases/download/v1.22.0/kompose-linux-arm64 -o kompose
fi

if [ "${MACHINE_TYPE}" = "x86_64" ]; then
    curl -L https://github.com/kubernetes/kompose/releases/download/v1.22.0/kompose-linux-amd64 -o kompose
fi

chmod +x kompose
sudo mv ./kompose /usr/local/bin/kompose

# add autocomplete
sudo apt install bash-completion -y
echo "source <(kubectl completion bash)" >> ~/.bashrc
echo "source <(minikube completion bash)" >> ~/.bashrc
echo "source /usr/share/bash-completion/bash_completion" >> ~/.bashrc
source ~/.bashrc 

# add firewall rules
sudo ufw allow 22 # ssh
sudo ufw allow 8001 # dashboard
sudo ufw allow 8443 # minikube cert server port
sudo ufw allow 443 # https
sudo ufw allow 10250 # metrics-server
yes | sudo ufw enable

sudo ufw allow 5678 # debugpy
sudo ufw allow 3000 # grafana

# add startup Minikube
INSTALL_FOLDER="$(dirname $(readlink -f $0))"
sudo cp "$INSTALL_FOLDER/minikube.service" /etc/systemd/system/minikube.service
# sudo chmod +x /etc/systemd/system/minikube.service
chmod +x "$INSTALL_FOLDER/startupMinikube.sh" 
sudo systemctl enable minikube.service
sudo systemctl daemon-reload
echo "starting minikube service ..."
sudo systemctl start minikube.service

