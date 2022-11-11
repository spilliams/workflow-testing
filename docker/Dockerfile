# syntax=docker/dockerfile:1.2
FROM ubuntu:22.04@sha256:4b1d0c4a2d2aaf63b37111f34eb9fa89fa1bf53dd6e4ca954d47caebca4005c2

ARG TARGETPLATFORM
ARG TARGETOS
ARG TARGETARCH

ARG USER=dev
ARG UID=1000
ARG HOME_DIR=/home/${USER}

ENV IN_CONTAINER="true"
ENV ORIGINAL_PATH=$PATH
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

##################################
#  Install apt packages
##################################
# DL3008: we always want the latest of these very stable packages
# DL3009: The check is looking for rm -rf, but this is the same thing
# hadolint ignore=DL3008,DL3009
RUN set -ex && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    # These need no explanation
    curl \
    git \
    sudo \
    unzip \
    wget \
    # Use HTTPS for apt package download
    apt-transport-https \
    # Root certificates to trust for HTTPS connections
    ca-certificates \
    # Commit signing, Terraform binary signature verification
    gnupg2 \
    gpg-agent \
    dirmngr \
    # CLI JSON utility
    jq \
    # Python dependencies
    gcc \
    libbz2-dev \
    libffi-dev \
    liblzma-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libxml2-dev \
    libxmlsec1-dev \
    llvm \
    tk-dev \
    xz-utils \
    zlib1g-dev \
    # Shell script linter, also used by actionlint
    shellcheck \
    # For Git interaction with GitHub
    openssh-client \
    # Recursively list directories in tree format
    tree \
    # In case you want Vim
    vim \
    && \
    find /var/lib/apt/lists -delete -mindepth 1

##################################
#  Set up WORKDIR
##################################
WORKDIR /src
# Trust and init an empty git repo so that
# we can cache pre-commit hooks later
RUN set -ex && \
    git config --system --add safe.directory /src && \
    git init --quiet

##################################
# Add SSH keys to known hosts file (for Git)
##################################
RUN set -ex && \
    ssh-keyscan github.com >> /etc/ssh/known_hosts

##################################
#  Create non-root user
##################################
# SC2016: $PATH is meant literally here
# hadolint ignore=SC2016
RUN set -ex && \
    groupadd --gid $UID $USER && \
    useradd --uid $UID -m --gid $UID -s /bin/bash $USER && \
    chown ${USER}:${USER} /src && \
    # the user needs to be able to chown the ssh socket later
    echo "${USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    # Alias sudo so that the env vars are inherited from the calling user
    echo 'alias sudo="sudo --preserve-env env PATH=$PATH"' >> $HOME_DIR/.bash_aliases && \
    chown ${USER}:${USER} $HOME_DIR/.bash_aliases

##################################
#  Install Golang
##################################
# ENV PATH="/usr/local/go/bin:${PATH}"
# # Since Golang releases pre-compiled binaries for each
# # OS + arch, and Docker just builds those binaries into the
# # default golang image, we can just copy over the files.
# COPY --from=golang /usr/local/go /usr/local/go

##################################
#  Install Python
##################################
# ENV PYENV_ROOT="/usr/local/pyenv"
# ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"
# COPY docker/.python-version .
# RUN set -ex && \
#     # Set this env var so that root sees it inside the container
#     echo "export PYENV_ROOT=${PYENV_ROOT}" >> /root/.bashrc && \
#     git clone https://github.com/pyenv/pyenv.git $PYENV_ROOT && \
#     pyenv install && \
#     eval "$(pyenv init -)"

##################################
#  Install pipx
##################################
# renovate: datasource=pypi depName=pipx
# ARG PIPX_VERSION=1.1.0
# ENV PIP_NO_CACHE_DIR=1
# ENV PIPX_HOME=/usr/local/pipx
# ENV PIPX_BIN_DIR=$PIPX_HOME/bin
# ENV PATH="${PIPX_BIN_DIR}:${PATH}"
# RUN set -ex && \
#     # Set these env vars so that root sees them inside the container
#     echo "export PIP_NO_CACHE_DIR=${PIP_NO_CACHE_DIR}" >> /root/.bashrc && \
#     echo "export PIPX_HOME=${PIPX_HOME}" >> /root/.bashrc && \
#     echo "export PIPX_BIN_DIR=${PIPX_BIN_DIR}" >> /root/.bashrc && \
#     # Don't install with --user here, else any modifications
#     # to site-packages during package installs will happen outside
#     # of pyenv
#     pip install pipx==${PIPX_VERSION}

##################################
#  Install Python CLI tools
##################################
# COPY docker/pipx_requirements.txt .
# RUN set -ex && \
#     xargs -a pipx_requirements.txt -I {} pipx install {}

##################################
#  Install poetry
##################################
# renovate: datasource=github-releases depName=python-poetry/poetry
# ARG POETRY_VERSION=1.2.2
# ENV POETRY_HOME=/usr/local/poetry
# ENV PATH="${POETRY_HOME}/bin:${PATH}"
# RUN set -ex && \
#     # Set this env var so that root sees it inside the container
#     echo "export POETRY_HOME=${POETRY_HOME}" >> /root/.bashrc && \
#     # Poetry binds to whatever version of Python it was installed with. So if the Python version
#     # is different than the upstream Docker image, re-install Poetry (forcibly) to pick up the new version
#     curl -sSL https://install.python-poetry.org | python3 - --force --version ${POETRY_VERSION} && \
#     pyenv rehash

##################################
#  Install Python packages
##################################
# COPY docker/pyproject.toml .
# COPY docker/poetry.lock .
# COPY docker/poetry.toml .
# RUN set -ex && \
#     poetry install --no-root --verbose && \
#     pyenv rehash

##################################
#  Install pre-commit hooks
##################################
# ENV PRE_COMMIT_HOME="/usr/local/pre-commit/cache"
# COPY docker/.pre-commit-config.yaml .
# RUN set -ex && \
#     # Set this env var so that root sees it inside the container
#     echo "export PRE_COMMIT_HOME=${PRE_COMMIT_HOME}" >> /root/.bashrc && \
#     pre-commit install-hooks && \
#     chmod 755 $PRE_COMMIT_HOME/repo* && \
#     mkdir -p $HOME_DIR/.cache/pre-commit && \
#     mv $PRE_COMMIT_HOME/db.db $HOME_DIR/.cache/pre-commit && \
#     chown -R $USER:$USER $HOME_DIR/.cache/pre-commit && \
#     ln -s $HOME_DIR/.cache/pre-commit/db.db $PRE_COMMIT_HOME/db.db

##################################
#  Install Terraform
##################################
ENV PATH="/usr/local/tfenv/bin:${PATH}"
ENV TF_PLUGIN_CACHE_DIR="${HOME_DIR}/.terraform.d/plugin-cache"
ENV TFENV_HOME=/usr/local/tfenv
COPY docker/.terraform-version .
RUN set -ex && \
    mkdir -p $TF_PLUGIN_CACHE_DIR && \
    chown $USER:$USER ${TF_PLUGIN_CACHE_DIR} && \
    git clone --depth 1 https://github.com/tfutils/tfenv.git ${TFENV_HOME} && \
    echo 'trust-tfenv: yes' > $TFENV_HOME/use-gpgv && \
    tfenv install && tfenv use

##################################
#  Install Terragrunt
##################################
COPY --chown=$UID:$UID docker/.terragrunt-version .
ENV PATH="/usr/local/tgenv/bin:${PATH}"
ENV TGENV_HOME=/usr/local/tgenv
RUN set -ex && \
    git clone --depth 1 https://github.com/taosmountain/tgenv.git ${TGENV_HOME} && \
    tgenv install && tgenv use

##################################
#  Install Lacework CLI
##################################
# RUN set -ex && \
#     curl https://raw.githubusercontent.com/lacework/go-sdk/main/cli/install.sh | bash

##################################
#  Install fixuid
##################################
# renovate: datasource=github-releases depName=boxboat/fixuid
ARG FIXUID_VERSION=v0.5.1
RUN set -ex && \
    curl -SsL https://github.com/boxboat/fixuid/releases/download/${FIXUID_VERSION}/fixuid-${FIXUID_VERSION#v}-${TARGETOS}-${TARGETARCH}.tar.gz | \
    tar -C /usr/local/bin -xzf - && \
    chown root:root /usr/local/bin/fixuid && \
    chmod 4755 /usr/local/bin/fixuid && \
    mkdir -p /etc/fixuid && \
    printf "user: %s\ngroup: %s\npaths:\n  - %s\n" "$USER" "$USER" "$HOME_DIR" > /etc/fixuid/config.yml

#################################
# Install terraform-docs
#################################
# # renovate: datasource=github-releases depName=terraform-docs/terraform-docs
# ARG TERRAFORM_DOCS_VERSION=v0.16.0
# RUN set -ex && \
#     wget -nv -P /tmp/ https://github.com/terraform-docs/terraform-docs/releases/download/${TERRAFORM_DOCS_VERSION}/terraform-docs-${TERRAFORM_DOCS_VERSION}-${TARGETOS}-${TARGETARCH}.tar.gz && \
#     tar -xzf /tmp/terraform-docs*.tar.gz && \
#     rm /tmp/terraform-docs*.tar.gz && \
#     chmod 755 terraform-docs && \
#     mv terraform-docs /usr/local/bin

##################################
#  Install tfmigrate
##################################
# # renovate: datasource=github-releases depName=minamijoyo/tfmigrate
# ARG TFMIGRATE_VERSION=v0.3.8
# RUN set -ex && \
#     wget -nv -P /tmp/ https://github.com/minamijoyo/tfmigrate/releases/download/${TFMIGRATE_VERSION}/tfmigrate_${TFMIGRATE_VERSION#v}_${TARGETOS}_${TARGETARCH}.tar.gz && \
#     tar -xzf /tmp/tfmigrate*.tar.gz && \
#     rm /tmp/tfmigrate*.tar.gz && \
#     chmod 755 tfmigrate && \
#     mv tfmigrate /usr/local/bin

##################################
#  Install hadolint
##################################
# # renovate: datasource=github-releases depName=hadolint/hadolint
# ARG HADOLINT_VERSION=v2.10.0
# RUN set -ex && \
#     case $TARGETPLATFORM in \
#     linux/amd64) \
#     hadolint_platform=Linux-x86_64;; \
#     linux/arm64) \
#     hadolint_platform=Linux-arm64;; \
#     esac && \
#     wget -nv -O /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/download/${HADOLINT_VERSION}/hadolint-${hadolint_platform} && \
#     chmod 755 /usr/local/bin/hadolint

##################################
#  Install actionlint
##################################
# # renovate: datasource=github-releases depName=rhysd/actionlint
# ARG ACTIONLINT_VERSION=v1.6.22
# RUN set -ex && \
#     wget -nv -P /tmp/ https://github.com/rhysd/actionlint/releases/download/${ACTIONLINT_VERSION}/actionlint_${ACTIONLINT_VERSION#v}_${TARGETOS}_${TARGETARCH}.tar.gz && \
#     tar -xzf /tmp/actionlint*.tar.gz && \
#     rm /tmp/actionlint*.tar.gz && \
#     chmod 755 actionlint && \
#     mv actionlint /usr/local/bin

##################################
#  Set $PATH and other env vars for root
##################################
# SC2016: The second $PATH is meant literally here
# hadolint ignore=SC2016
RUN set -ex && \
    # export PATH=/foo/bar:${PATH}
    echo 'export PATH='${PATH%"${ORIGINAL_PATH}"}'${PATH}' >> /root/.bashrc

##################################
#  Switch to non-root user
##################################
USER ${USER}:${USER}
ENV PATH="${HOME_DIR}/.local/bin:${PATH}"

##################################
# Set ENTRYPOINT to fix UID/GID permissions of $HOME
##################################
ENTRYPOINT [ "/usr/local/bin/fixuid", "-q" ]
CMD [ "/bin/bash" ]
