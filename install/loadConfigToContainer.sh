#!/bin/bash
HOST="192.168.178.3"
# print_usage() {
#   printf "Usage: ...\n"
# }

while getopts 'h:' flag; do
  case "${flag}" in
    h) HOST=$OPTARG;;
    # *) print_usage
    #    exit 1 ;;
  esac
done

LOCAL_IPV4="$(hostname -I | awk '{print $1}')"
echo "load config from ${HOST} to ${LOCAL_IPV4}"

scp ubuntu@${HOST}:~/.kube/config ~/.kube/config >/dev/null

scp ubuntu@${HOST}:~/.minikube/ca.crt ~/.minikube >/dev/null
scp ubuntu@${HOST}:~/.minikube/profiles/minikube/client.crt ~/.minikube >/dev/null
scp ubuntu@${HOST}:~/.minikube/profiles/minikube/client.key ~/.minikube >/dev/null

# Point .kube/config to the correct locaiton of the certs
sed -i -r "s|(\s*certificate-authority:\s).*|\\1$HOME\/.minikube\/ca.crt|g" $HOME/.kube/config
sed -i -r "s|(\s*client-certificate:\s).*|\\1$HOME\/.minikube\/client.crt|g" $HOME/.kube/config
sed -i -r "s|(\s*client-key:\s).*|\\1$HOME\/.minikube\/client.key|g" $HOME/.kube/config
