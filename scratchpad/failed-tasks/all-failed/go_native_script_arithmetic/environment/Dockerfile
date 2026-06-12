FROM ubuntu:24.04

# System packages, Node.js v24 (required by windmill-cli), Go toolchain,
# the Windmill CLI itself, and the Python verification dependencies.
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep \
        build-essential xz-utils && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g windmill-cli && \
    curl -fsSL https://go.dev/dl/go1.22.6.linux-amd64.tar.gz -o /tmp/go.tar.gz && \
    tar -C /usr/local -xzf /tmp/go.tar.gz && \
    rm /tmp/go.tar.gz && \
    ln -s /usr/local/go/bin/go /usr/local/bin/go && \
    ln -s /usr/local/go/bin/gofmt /usr/local/bin/gofmt && \
    pip3 install --break-system-packages pytest-json-ctrf && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/local/go/bin:${PATH}"
ENV GOPATH="/root/go"

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject

LABEL Author="generate-harbor-tasks"
LABEL Description="Windmill cloud CLI task environment with Go toolchain, Node.js v24, and windmill-cli for authoring and deploying Go-native scripts."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (required by windmill-cli)
#   - windmill-cli installed globally via npm (provides `wmill`)
#   - Go 1.22 toolchain at /usr/local/go (PATH updated; `go` symlinked into /usr/local/bin)
#   - /home/user/myproject: pre-created project directory used by the executor and tests
#   - Workspace registration (`evaluation-ws` against https://app.windmill.dev) is performed
#     at initial-state-test time using the runtime WMILL_TOKEN.
