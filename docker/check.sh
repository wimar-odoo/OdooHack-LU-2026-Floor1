#!/bin/sh
# Trivi'Hackathon 2026: check that Docker is ready, and say what to do when it is not.
# Run by `make check`, and before every make command (--quiet: say nothing when all is fine).
cd "$(dirname "$0")/.." || exit 1
quiet=; [ "$1" = --quiet ] && quiet=1
wsl=; [ "$(uname)" = Linux ] && grep -qi microsoft /proc/version 2>/dev/null && wsl=1
wsl_integration="With Docker Desktop: Settings > Resources > WSL integration, enable your distribution (e.g. Ubuntu), Apply, then open a new terminal."

if ! command -v docker >/dev/null 2>&1; then
    if [ -n "$wsl" ]; then echo "Docker is not found in WSL. $wsl_integration Without Docker Desktop: install Docker Engine in WSL (PRE-REQUISITES.md)."
    else echo "Docker is not installed: see PRE-REQUISITES.md."; fi
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "The command 'docker compose' (version 2) is missing."
    if command -v brew >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1; then
        echo "  Homebrew: mkdir -p ~/.docker/cli-plugins && ln -sfn \"$(command -v docker-compose)\" ~/.docker/cli-plugins/docker-compose"
    elif command -v apt-get >/dev/null 2>&1; then
        echo "  Ubuntu / Debian: sudo apt install docker-compose-plugin (packages of docs.docker.com) or docker-compose-v2 (packages of Ubuntu)"
    fi
    exit 1
fi

if ! error=$(docker version 2>&1 >/dev/null); then
    context=$(docker context show 2>/dev/null)
    echo "Docker does not answer (Docker context: ${context:-unknown}):"
    echo "$error" | grep -v '^$' | head -n 3 | sed 's/^/  /'
    case "$error $context" in
        *WSL*) echo "$wsl_integration" ;;
        *colima*) echo "Start Colima: colima start --cpu 4 --memory 6 (again after each restart of the computer)." ;;
        *"ermission denied"*)
            if grep '^docker:' /etc/group 2>/dev/null | cut -d: -f4 | tr , '\n' | grep -qx "$(id -un)"; then
                echo "You are in the docker group, but not yet in this session: log out and back in (or, in this terminal only: newgrp docker)."
            else
                echo "Add yourself to the docker group: sudo usermod -aG docker \$USER, then log out and back in (or, in this terminal only: newgrp docker)."
            fi ;;
        *)
            if command -v colima >/dev/null 2>&1; then
                echo "Start Colima: colima start --cpu 4 --memory 6 (or Docker Desktop, if that is the one you use)."
            elif systemctl list-unit-files docker.service 2>/dev/null | grep -q '^docker.service'; then
                echo "Start Docker Engine: sudo systemctl start docker (sudo systemctl enable --now docker: also when the computer starts)."
            elif [ -n "$wsl" ] && [ -x /etc/init.d/docker ]; then
                echo "Start Docker Engine: sudo service docker start (or enable systemd in WSL: see PRE-REQUISITES.md)."
            else
                echo "Start Docker Desktop (or your Docker engine), and wait until it says that it is running."
            fi ;;
    esac
    echo "Several Docker installations (Docker Desktop, Colima, Docker Engine)? 'docker context ls' lists them, 'docker context use <name>' picks the one that runs."
    exit 1
fi

# the warnings below don't stop anything
memory=$(docker info --format '{{.MemTotal}}' 2>/dev/null)
if [ "${memory:-0}" -gt 0 ] 2>/dev/null && [ "$memory" -lt 3000000000 ]; then
    echo "Warning: Docker has only $((memory / 1000000)) MB of memory, 4 GB are advised (or the installation may be killed, exit code 137)."
    echo "  Colima: colima stop && colima start --cpu 4 --memory 6 / Docker Desktop: Settings > Resources > Memory"
fi
if [ "$(uname)" = Linux ]; then
    # Odoo runs as another user in the container (odoo): it must be able to read the files of the repository.
    # Private files (e.g. cloned with a umask 077): Odoo cannot start at all without the folder and docker/.
    fix="in the folder of the repository: chmod -R a+rX . (its files are private, e.g. because of a umask 077)"
    blocking=$(find . docker docker/start.sh docker/odoo.conf -maxdepth 0 \( -type d ! -perm -005 -o -type f ! -perm -004 \) 2>/dev/null | head -n 1)
    unreadable=$(find trivia_* \( -type d ! -perm -005 -o -type f ! -perm -004 \) 2>/dev/null | head -n 1)
    if [ -n "$blocking" ]; then
        [ "$blocking" = . ] && blocking="the folder of the repository"
        echo "Odoo (user odoo in its container) cannot read $blocking. Fix, $fix."
        exit 1
    elif [ -n "$unreadable" ]; then
        echo "Warning: Odoo (user odoo in its container) cannot read $unreadable. Fix, $fix."
    fi
fi
if [ -n "$wsl" ]; then
    case "$(pwd)" in
        /mnt/*) echo "Warning: the repository is on the Windows disk ($(pwd)): clone it in your WSL home folder (cd ~) instead, it is much faster." ;;
    esac
fi
if [ -z "$quiet" ]; then
    echo "Docker is ready."
fi
