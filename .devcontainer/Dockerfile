# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.158.0/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version: 3, 3.9, 3.8, 3.7, 3.6
ARG VARIANT="3"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# [Option] Install Node.js
ARG INSTALL_NODE="true"
ARG NODE_VERSION="lts/*"
RUN if [ "${INSTALL_NODE}" = "true" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
COPY docker/requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g <your-package-here>" 2>&1

# Docker from Docker
# https://github.com/microsoft/vscode-dev-containers/tree/master/containers/docker-from-docker
# Install Docker CE CLI
RUN apt-get update \
    && apt-get install -y apt-transport-https ca-certificates curl gnupg2 lsb-release \
    && curl -fsSL https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]')/gpg | apt-key add - 2>/dev/null \
    && echo "deb [arch=amd64] https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]') $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce-cli

# Install Docker Compose
RUN LATEST_COMPOSE_VERSION=$(curl -sSL "https://api.github.com/repos/docker/compose/releases/latest" | grep -o -P '(?<="tag_name": ").+(?=")') \
    && curl -sSL "https://github.com/docker/compose/releases/download/${LATEST_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose \
    && sudo curl \
    -L "https://raw.githubusercontent.com/docker/compose/${LATEST_COMPOSE_VERSION}/contrib/completion/bash/docker-compose" \
    -o /etc/bash_completion.d/docker-compose

# Install kubectl
RUN curl -sSL -o /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl \
    && chmod +x /usr/local/bin/kubectl

# Install Helm
RUN curl -s https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash -

COPY .devcontainer/copy-kube-config.sh /usr/local/share/
RUN echo "source /usr/local/share/copy-kube-config.sh" | tee -a /root/.bashrc >> /root/.zshrc
    
# add bash history
RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
    && echo $SNIPPET >> "/root/.bashrc"

# add minikube
RUN curl -L https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 \
    -o /usr/local/bin/minikube \
    && chmod +x /usr/local/bin/minikube

# add kompose
RUN curl -L https://github.com/kubernetes/kompose/releases/download/v1.22.0/kompose-linux-amd64 -o kompose \
    && chmod +x kompose \
    && sudo mv ./kompose /usr/local/bin/kompose

# add autocompletion
SHELL ["/bin/bash", "-c"]
RUN apt install bash-completion -y \
    && echo "source <(kubectl completion bash)" >> ~/.bashrc \
    && echo "source /usr/share/bash-completion/bash_completion" >> ~/.bashrc \
    && echo "source <(minikube completion bash)" >> ~/.bashrc