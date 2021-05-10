#!/bin/bash
scp ubuntu@192.168.178.7:~/.kube/config ~/.kube/config

scp ubuntu@192.168.178.7:~/.minikube/ca.crt ~/.minikube
scp ubuntu@192.168.178.7:~/.minikube/profiles/minikube/client.crt ~/.minikube
scp ubuntu@192.168.178.7:~/.minikube/profiles/minikube/client.key ~/.minikube

# Point .kube/config to the correct locaiton of the certs
sed -i -r "s|(\s*certificate-authority:\s).*|\\1$HOME\/.minikube\/ca.crt|g" $HOME/.kube/config
sed -i -r "s|(\s*client-certificate:\s).*|\\1$HOME\/.minikube\/client.crt|g" $HOME/.kube/config
sed -i -r "s|(\s*client-key:\s).*|\\1$HOME\/.minikube\/client.key|g" $HOME/.kube/config
