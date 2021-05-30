#!/bin/bash
# get local ip
LOCAL_IPV4="$(hostname -I | awk '{print $1}')" 

# start minikube
/usr/local/bin/minikube start --vm-driver=none --apiserver-ips="${LOCAL_IPV4}"

# start dashboard
timeout 7s minikube dashboard

# enable metrics
minikube addons enable metrics-server
