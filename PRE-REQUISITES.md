<div align="center">

# 🧀 Trivi'Hackathon 2026

**Prerequisites · Pré-requis**

Get your computer ready before the day<br>
Préparez votre ordinateur avant le jour J

⏱️ ~30 min &nbsp;·&nbsp; 🪟 Windows &nbsp;·&nbsp; 🍎 macOS &nbsp;·&nbsp; 🐧 Linux

**[🇬🇧 English](#-english)** &nbsp;&nbsp;|&nbsp;&nbsp; **[🇫🇷 Français](#-français)**

</div>

---

## 🇬🇧 English

### 🎯 1. Before the hackathon

On the day, you will write and test your code **on your computer**, in an Odoo that runs in Docker. To spend the day on the challenges and not on installations, get your computer ready **now** with this guide. It takes **about 30 minutes**, mostly downloads.

| | Step | Where |
|:-:|---|---|
| 1 | Install the tools (Git, Docker, make), and check each of them | [section 3](#-3-install-the-tools) |
| 2 | Connect Git to your GitHub account, to push your work on the day | [section 4](#-4-connect-git-to-github) |
| 3 | Get this repository, and start your first Odoo, with an empty database | [sections 5](#-5-get-the-repository) and [6](#-6-start-odoo-for-the-first-time) |
| 4 | Check that you can open the GitHub repository and the Odoo.sh project | [section 7](#-7-check-your-access) |
| ✅ | Tick the final checklist | [section 9](#-9-final-checklist) |

> [!NOTE]
> The **challenges are not here yet**: this branch only holds what is needed to run Odoo. You will get them on the day, on a computer that is ready.

💡 Git, Docker Compose 2 and make already installed? Run the checks of your system in [section 3](#-3-install-the-tools), then go on with [section 4](#-4-connect-git-to-github).

### 🧰 2. What you need

**💻 A computer** on which you can install software, with:

- **8 GB of RAM**, 4 GB of them for Docker
- **10 GB of free disk space**

**🧰 The tools**, installed in [section 3](#-3-install-the-tools):

| Tool | What for |
|---|---|
| **Git** | get the code, and push your work on the day |
| **Docker** and **Docker Compose** (version 2) | run Odoo 20 and PostgreSQL, the same for everyone |
| **make** | the short commands of the project: `make init`, `make up`... |

**✏️ Your favourite code editor or IDE** (VS Code, PyCharm...), installed on this computer: you will write Python and XML.

**👤 Two accesses:**

- a **GitHub account**, the one whose user name you gave to the organisers: on the day, it gets the right to push to the repository. The repository is public: <https://github.com/wimar-odoo/OdooHack-LU-2026>
- the **Odoo.sh** project <https://www.odoo.sh/project/odoo-ps-hackathon26>, given by an invitation e-mail from the organisers ([section 7](#-7-check-your-access)).

### 🔧 3. Install the tools

Open the section of your system, and follow its steps in order: each tool comes with the commands that check it.

> [!NOTE]
> **Docker Desktop** (Windows, macOS) is free for personal use, education, and companies with fewer than 250 employees and less than 10 million USD of revenue. You use it for a larger company? Check that it has a Docker subscription, or take the free alternative of your system below.

<details>
<summary><b>🪟 Windows</b></summary>

<br>

Two ways, pick one:

- **Docker Desktop** (recommended): steps 1️⃣ to 4️⃣ below;
- **WSL 2 and Docker Engine** (free, without Docker Desktop): the block **🆓 Windows, free alternative** at the end of this section.

Work in **Windows Terminal** (included in Windows 11, in the Microsoft Store for Windows 10), in a **PowerShell** or **Git Bash** tab.

**1️⃣ Git for Windows** (it brings Git Bash). In PowerShell:

```powershell
winget install --id Git.Git -e --source winget
```

Or download its installer from <https://git-scm.com/install/windows>, and keep the default options.

**2️⃣ Docker Desktop**

1. Download it from <https://docs.docker.com/desktop/setup/install/windows-install/>.
2. Install it with the option **Use WSL 2** checked, and restart Windows.
3. Start Docker Desktop, and wait until it says *Engine running*. It asks to install or update WSL? Accept.

> 💡 Docker Desktop says *You are not allowed to use Docker, you must be in the "docker-users" group*? In a PowerShell opened **as administrator**, run this command (replace `<your Windows user name>`), then log out of Windows and back in:
>
> ```powershell
> net localgroup docker-users <your Windows user name> /add
> ```

**3️⃣ make**. In PowerShell:

```powershell
winget install ezwinports.make
```

**4️⃣ Check**. First **close the terminal and open a new one**: the new commands are only found in a new terminal. Then:

```powershell
git --version
make --version
docker --version
docker compose version
docker run --rm hello-world
```

✅ `docker compose version` shows version **2** or more, and `hello-world` prints *Hello from Docker!*

> ⚠️ In [section 5](#-5-get-the-repository), clone the repository in a folder that is **not synchronised by OneDrive** (*Documents* and *Desktop* often are), e.g. `C:\dev`.

<details>
<summary><b>🆓 Windows, free alternative: WSL 2 and Docker Engine, without Docker Desktop</b></summary>

<br>

Everything then happens in **Ubuntu**, a Linux inside Windows, with the same commands as Linux. Follow these steps instead of steps 1️⃣ to 4️⃣ above.

**1️⃣ WSL and Ubuntu**. In a PowerShell opened **as administrator**, then restart Windows:

```powershell
wsl --install
```

Open **Ubuntu** (Start menu, or a tab of Windows Terminal), and choose a Linux user name and password.

✅ Check in PowerShell: `wsl --list --verbose` shows Ubuntu with the VERSION **2**.

**2️⃣ systemd**, which starts Docker.

✅ Check in Ubuntu: `ps -p 1 -o comm=` prints `systemd` (the default for Ubuntu installed with `wsl --install`).

It does not? Add these lines to `/etc/wsl.conf` (`sudo nano /etc/wsl.conf`), run `wsl --shutdown` in PowerShell, and open Ubuntu again:

```ini
[boot]
systemd=true
```

**3️⃣ Git, make and Docker Engine**: in Ubuntu, follow the **🐧 Linux** section below, with its Ubuntu commands. When it says to restart the computer: close Ubuntu, run `wsl --shutdown` in PowerShell, and open Ubuntu again.

> ⚠️ In [section 5](#-5-get-the-repository), clone the repository **in your Ubuntu home folder** (`cd ~`), not in `/mnt/c/...`: it is much faster. All the commands of this guide then run in Ubuntu.

</details>

</details>

<details>
<summary><b>🍎 macOS</b></summary>

<br>

**1️⃣ Git and make** come with the Command Line Tools of Apple (*already installed*? fine):

```sh
xcode-select --install
```

Check:

```sh
git --version
make --version
```

**2️⃣ Docker**, one of the two:

- **Docker Desktop** (recommended): download it from <https://docs.docker.com/desktop/setup/install/mac-install/>, the version of your chip (Apple or Intel: Apple menu › About This Mac). Start it, and wait until it says *Engine running*.
- **Colima**, the free alternative, in command line only: open the block below.

<details>
<summary><b>🆓 macOS, free alternative: Colima</b></summary>

<br>

Colima is installed with Homebrew: `brew --version` does not answer? Install Homebrew first with the command of <https://brew.sh>, and follow the *Next steps* that it prints. Then:

```sh
brew install colima docker docker-compose
mkdir -p ~/.docker/cli-plugins
ln -sfn "$(brew --prefix)/opt/docker-compose/bin/docker-compose" ~/.docker/cli-plugins/docker-compose
colima start --cpu 4 --memory 6
```

> ⚠️ Colima does not start by itself: run `colima start --cpu 4 --memory 6` again after each restart of your Mac.

</details>

**3️⃣ Check**:

```sh
docker --version
docker compose version
docker run --rm hello-world
```

✅ `docker compose version` shows version **2** or more, and `hello-world` prints *Hello from Docker!*

</details>

<details>
<summary><b>🐧 Linux</b></summary>

<br>

The commands below are for **Ubuntu** (22.04 or more recent). Fedora: see the block at the end of this section. Debian and the other distributions: <https://docs.docker.com/engine/install/>, choose yours.

> ⚠️ Don't use the *snap* of Docker, nor Docker Desktop: Docker Engine is enough.

**1️⃣ Git and make**:

```sh
sudo apt update
sudo apt install -y git make
```

Check:

```sh
git --version
make --version
```

**2️⃣ Docker Engine** and its compose plugin, from the repository of Docker (official instructions: <https://docs.docker.com/engine/install/ubuntu/>).

First remove the unofficial packages, if any:

```sh
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc docker-buildx podman-docker containerd runc | cut -f1)
```

Add the repository of Docker:

```sh
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
```

Install Docker Engine, the `docker` command and its compose plugin (Docker then starts by itself, also when the computer starts):

```sh
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

**3️⃣ Docker without sudo**: join the `docker` group:

```sh
sudo usermod -aG docker $USER
```

> ⚠️ Then **restart the computer** (closing the terminal is not enough): until then, Docker answers *permission denied*. To use Docker right away, in the current terminal only: `newgrp docker`.

**4️⃣ Check**, without `sudo`:

```sh
docker --version
docker compose version
docker run --rm hello-world
```

✅ `docker compose version` shows version **2** or more, and `hello-world` prints *Hello from Docker!*

<details>
<summary><b>🐧 Linux, Fedora</b></summary>

<br>

Git and make:

```sh
sudo dnf install -y git make
```

Docker Engine (official instructions: <https://docs.docker.com/engine/install/fedora/>):

```sh
sudo dnf config-manager addrepo --from-repofile https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

Then steps 3️⃣ and 4️⃣ above.

</details>

</details>

### 🔐 4. Connect Git to GitHub

On the day, each team pushes its work to its own branch of the repository, so that the organisers can check it. They give the right to push to the GitHub account that you gave them: prepare your computer to sign in with it. In your terminal (Windows: Git Bash or PowerShell; with WSL: Ubuntu):

**1️⃣ Your identity**, written in each of your commits:

```sh
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Use an e-mail address of your GitHub account (<https://github.com/settings/emails>), so that your commits are linked to you. Your address is private there (*Keep my email addresses private*)? Use the `...@users.noreply.github.com` address that this page shows.

✅ `git config --global user.email` prints this address.

**2️⃣ An SSH key**, with which Git signs in to GitHub without a password. You already have one on your GitHub account? Go to step 3️⃣. Otherwise, create it (press Enter at each question; a passphrase is optional):

```sh
ssh-keygen -t ed25519 -C "you@example.com"
```

Show its public part:

```sh
cat ~/.ssh/id_ed25519.pub
```

> 💡 Windows says *'cat' is not recognized as an internal or external command*? You are in a Command Prompt (cmd), not in PowerShell: run `type %USERPROFILE%\.ssh\id_ed25519.pub` instead.

Copy the whole line, and add it to your GitHub account: <https://github.com/settings/keys> › **New SSH key**, paste it in *Key*, then **Add SSH key**.

**3️⃣ Check** (the first time, answer `yes` to the question about the authenticity of github.com):

```sh
ssh -T git@github.com
```

✅ It answers *Hi \<your GitHub user name\>! You've successfully authenticated, but GitHub does not provide shell access.*, with the user name that you gave to the organisers.

> [!NOTE]
> You already push to GitHub over HTTPS from this computer (GitHub CLI, Git Credential Manager...)? You can keep it: in [section 5](#-5-get-the-repository), clone with `https://github.com/wimar-odoo/OdooHack-LU-2026.git` instead.

### 📥 5. Get the repository

In the folder of your choice:

- **Windows**: outside OneDrive, e.g. `C:\dev`;
- **WSL**: in Ubuntu, `cd ~`.

```sh
git clone -b 20.0-pre_hackathon_setup git@github.com:wimar-odoo/OdooHack-LU-2026.git
cd OdooHack-LU-2026
git branch --show-current
```

✅ The last command prints `20.0-pre_hackathon_setup`.

In the folder:

```text
OdooHack-LU-2026/
├── Makefile             the make commands (make help lists them)
├── docker-compose.yml   the two containers: Odoo 20 and PostgreSQL 16
├── docker/
│   ├── odoo.conf        the configuration of Odoo
│   ├── start.sh         how it starts
│   └── check.sh         the checks of make check
└── PRE-REQUISITES.md    this guide
```

On the day, the modules of the challenges (folders `trivia_*`) will come next to these files.

### 🚀 6. Start Odoo for the first time

In the folder of the repository:

```sh
make check
make init
```

- **`make check`** must answer *Docker is ready.* Otherwise, it says what to do.
- **`make init`** downloads Odoo and PostgreSQL (about 1 GB, only the first time), then creates an empty database: *no trivia_\* module yet, creating the database* is normal. It ends once Odoo answers: a few minutes the first time.

Then:

1. open <http://localhost:8069>;
2. log in with `admin` / `admin`;
3. ✅ you are in Odoo, without any app yet.

**The commands of every day**, to try now:

| Command | What |
|---|---|
| `make down` | Stop Odoo (the database is kept) |
| `make up` | Start Odoo again |
| `make logs` | Follow the logs of Odoo (`Ctrl+C` to quit) |
| `make help` | List all the commands |

> [!TIP]
> Until the hackathon, you can stop Odoo with `make down`. Keep the folder: the downloads and the database will be used on the day.

### 🔑 7. Check your access

**GitHub**: <https://github.com/wimar-odoo/OdooHack-LU-2026> opens. It is public: no invitation is needed to read it, and your `git clone` already used it. The right to push comes on the day: GitHub then sends an invitation to the account that you gave to the organisers. Accept it, from its e-mail or on <https://github.com/wimar-odoo/OdooHack-LU-2026/invitations>.

**Odoo.sh**:

1. wait for the invitation e-mail of the organisers;
2. sign in on <https://www.odoo.sh> with your GitHub account (the one you gave to the organisers);
3. open <https://www.odoo.sh/project/odoo-ps-hackathon26>: ✅ you see the project.

Access refused, or still no invitation a few days before the hackathon? [Contact us](#-10-contact-us).

### 🩹 8. Troubleshooting

> [!TIP]
> Run `make check` first: it finds most problems, and says what to do.

Click on your problem:

<details>
<summary><b>Windows: the virtualisation is disabled</b>: <code>Virtualization support not detected</code>, <code>0x80370102</code></summary>

<br>

Docker Desktop and WSL 2 need the virtualisation of the processor. Check it in the Task Manager › **Performance** › **CPU**: *Virtualization* must say *Enabled*.

It says *Disabled*? Enable it in the BIOS/UEFI of your computer (restart it, and press the key shown at startup, often F2, F10, Del or Esc). Depending on the manufacturer, the option is called *Intel Virtualization Technology* (VT-x) or *SVM Mode* (AMD). On a computer of your company, ask its IT department.

</details>

<details>
<summary><b>Docker does not answer</b>: <code>Cannot connect to the Docker daemon</code>, <code>failed to connect to the docker API</code></summary>

<br>

Start it:

- **Docker Desktop**: wait until it says *Engine running*;
- **Colima**: `colima start --cpu 4 --memory 6`;
- **Linux and WSL**: `sudo systemctl start docker`.

</details>

<details>
<summary><code>permission denied</code> on <code>/var/run/docker.sock</code> (Linux, WSL)</summary>

<br>

Your terminal does not know yet that you are in the `docker` group:

1. Join it (step 3️⃣ of the Linux section; no problem if it is already done): `sudo usermod -aG docker $USER`.
2. To fix it right away, in the current terminal only: `newgrp docker`.
3. To fix it for good, in all terminals: Linux: restart the computer (closing the terminal is not enough); WSL: `wsl --shutdown` in PowerShell, then open Ubuntu again.

</details>

<details>
<summary><code>you must be in the "docker-users" group</code> (Windows, Docker Desktop)</summary>

<br>

See step 2️⃣ of the Windows section.

</details>

<details>
<summary><code>make: command not found</code>, <code>make is not recognized</code></summary>

<br>

Install make ([section 3](#-3-install-the-tools)), then open a new terminal.

</details>

<details>
<summary><code>docker: 'compose' is not a docker command</code></summary>

<br>

Docker Compose version 2 is missing (the old `docker-compose`, version 1, is not enough):

- **Linux**: `sudo apt install docker-compose-plugin`;
- **macOS with Colima**: the `mkdir` and `ln -sfn` commands of the macOS section.

</details>

<details>
<summary><code>Permission denied (publickey)</code> (Git, GitHub)</summary>

<br>

GitHub does not know the SSH key of this computer: add it to your GitHub account, see step 2️⃣ of [section 4](#-4-connect-git-to-github), then run `ssh -T git@github.com` again.

</details>

<details>
<summary><code>ssh: connect to host github.com port 22</code>: <code>Connection timed out</code>, <code>Connection refused</code></summary>

<br>

The network blocks SSH (port 22), as some companies and public Wi-Fi do. GitHub also accepts SSH on the port 443: add these lines to the file `~/.ssh/config` (create it if needed), then run `ssh -T git@github.com` again:

```text
Host github.com
    Hostname ssh.github.com
    Port 443
    User git
```

</details>

<details>
<summary><b>Windows: Odoo is slow, or files are not found</b></summary>

<br>

Clone the repository outside OneDrive (e.g. `C:\dev`), or with WSL in your Ubuntu home folder, not in `/mnt/c`.

</details>

<details>
<summary><b>Line endings</b>: <code>$'\r': command not found</code>, <code>/bin/sh^M</code>, <code>bad interpreter</code></summary>

<br>

The repository keeps Unix line endings, but a tool converted them. Delete the folder and clone it again. With WSL, clone it in Ubuntu: don't copy it from Windows.

</details>

<details>
<summary><b>Odoo does not start</b>, <code>exited (137)</code></summary>

<br>

`make up` and `make init` show the end of the logs of Odoo, with the error; `make logs` shows all of them.

*exited (137)*: Docker lacks memory, give it at least 4 GB:

- **Docker Desktop**: Settings › Resources;
- **Colima**: `colima stop`, then `colima start --cpu 4 --memory 6`.

</details>

<details>
<summary><b>Port 8069 already used</b>: <code>port is already allocated</code>, <code>address already in use</code></summary>

<br>

Another program, maybe another Odoo, uses it. Stop it, or create a file `.env` next to `docker-compose.yml` with this line:

```ini
ODOO_PORT=8070
```

Then run `make up`, and open <http://localhost:8070>.

</details>

<details>
<summary><b>Containers already there, or something strange</b></summary>

<br>

Start over with `make reset` (it deletes the local database: no problem before the hackathon), then `make init`.

</details>

<details>
<summary><b>Windows:</b> <code>make shell</code> or <code>make psql</code> say <code>the input device is not a TTY</code></summary>

<br>

Run them in Windows Terminal, not in the Git Bash window.

</details>

### ✅ 9. Final checklist

- [ ] `git --version`, `make --version` and `docker compose version` (2 or more) answer
- [ ] `docker run --rm hello-world` prints *Hello from Docker!*, without `sudo`
- [ ] `git config --global user.email` prints an e-mail of your GitHub account, and `ssh -T git@github.com` answers *Hi \<your GitHub user name\>!*
- [ ] the repository is cloned, on the branch `20.0-pre_hackathon_setup`
- [ ] `make check` answers *Docker is ready.*
- [ ] `make init` ended, and <http://localhost:8069> opens with `admin` / `admin`
- [ ] <https://github.com/wimar-odoo/OdooHack-LU-2026> and <https://www.odoo.sh/project/odoo-ps-hackathon26> open
- [ ] your favourite code editor is installed

<div align="center">

**All ticked? Your computer is ready: see you on the day! 🧀**

</div>

### 📬 10. Contact us

A problem that this guide does not solve? Write to us, with the command that you ran and its whole output (a screenshot is fine):

> **William Marette**, Software Developer<br>
> ✉️ <wimar@odoo.com>

---

## 🇫🇷 Français

### 🎯 1. Avant le hackathon

Le jour J, vous écrirez et testerez votre code **sur votre ordinateur**, dans un Odoo qui tourne dans Docker. Pour passer la journée sur les challenges et non sur des installations, préparez votre ordinateur **dès maintenant** avec ce guide. Comptez **environ 30 minutes**, surtout des téléchargements.

| | Étape | Où |
|:-:|---|---|
| 1 | Installez les outils (Git, Docker, make), en vérifiant chacun d'eux | [section 3](#-3-installer-les-outils) |
| 2 | Reliez Git à votre compte GitHub, pour pousser votre travail le jour J | [section 4](#-4-relier-git-à-github) |
| 3 | Récupérez ce dépôt, et lancez votre premier Odoo, avec une base vide | [sections 5](#-5-récupérer-le-dépôt) et [6](#-6-lancer-odoo-pour-la-première-fois) |
| 4 | Vérifiez que vous pouvez ouvrir le dépôt GitHub et le projet Odoo.sh | [section 7](#-7-vérifier-vos-accès) |
| ✅ | Cochez la checklist finale | [section 9](#-9-checklist-finale) |

> [!NOTE]
> Les **challenges ne sont pas encore là** : cette branche ne contient que le nécessaire pour faire tourner Odoo. Vous les recevrez le jour J, sur un ordinateur prêt.

💡 Git, Docker Compose 2 et make déjà installés ? Lancez les vérifications de votre système à la [section 3](#-3-installer-les-outils), puis passez à la [section 4](#-4-relier-git-à-github).

### 🧰 2. Ce qu'il vous faut

**💻 Un ordinateur** sur lequel vous pouvez installer des logiciels, avec :

- **8 Go de RAM**, dont 4 Go pour Docker
- **10 Go d'espace disque libre**

**🧰 Les outils**, installés à la [section 3](#-3-installer-les-outils) :

| Outil | Pour quoi faire |
|---|---|
| **Git** | récupérer le code, et pousser votre travail le jour J |
| **Docker** et **Docker Compose** (version 2) | faire tourner Odoo 20 et PostgreSQL, à l'identique pour tout le monde |
| **make** | les commandes courtes du projet : `make init`, `make up`... |

**✏️ Votre éditeur de code ou IDE préféré** (VS Code, PyCharm...), installé sur cet ordinateur : vous écrirez du Python et du XML.

**👤 Deux accès :**

- un **compte GitHub**, celui dont vous avez donné le nom d'utilisateur aux organisateurs : le jour J, il reçoit le droit de pousser sur le dépôt. Le dépôt est public : <https://github.com/wimar-odoo/OdooHack-LU-2026>
- le projet **Odoo.sh** <https://www.odoo.sh/project/odoo-ps-hackathon26>, donné par un e-mail d'invitation des organisateurs ([section 7](#-7-vérifier-vos-accès)).

### 🔧 3. Installer les outils

Ouvrez la section de votre système, et suivez ses étapes dans l'ordre : chaque outil est suivi des commandes qui le vérifient.

> [!NOTE]
> **Docker Desktop** (Windows, macOS) est gratuit pour un usage personnel, l'enseignement, et les entreprises de moins de 250 salariés et de moins de 10 millions USD de chiffre d'affaires. Vous l'utilisez pour une entreprise plus grande ? Vérifiez qu'elle a un abonnement Docker, ou prenez l'alternative gratuite de votre système ci-dessous.

<details>
<summary><b>🪟 Windows</b></summary>

<br>

Deux possibilités, au choix :

- **Docker Desktop** (recommandé) : étapes 1️⃣ à 4️⃣ ci-dessous ;
- **WSL 2 et Docker Engine** (gratuit, sans Docker Desktop) : le bloc **🆓 Windows, alternative gratuite** à la fin de cette section.

Travaillez dans **Windows Terminal** (inclus dans Windows 11, dans le Microsoft Store pour Windows 10), dans un onglet **PowerShell** ou **Git Bash**.

**1️⃣ Git for Windows** (il apporte Git Bash). Dans PowerShell :

```powershell
winget install --id Git.Git -e --source winget
```

Ou téléchargez son installateur sur <https://git-scm.com/install/windows>, et gardez les options par défaut.

**2️⃣ Docker Desktop**

1. Téléchargez-le sur <https://docs.docker.com/desktop/setup/install/windows-install/>.
2. Installez-le avec l'option **Use WSL 2** cochée, et redémarrez Windows.
3. Lancez Docker Desktop, et attendez qu'il affiche *Engine running*. Il demande d'installer ou de mettre à jour WSL ? Acceptez.

> 💡 Docker Desktop affiche *You are not allowed to use Docker, you must be in the "docker-users" group* ? Dans un PowerShell ouvert **en administrateur**, lancez cette commande (remplacez `<votre utilisateur Windows>`), puis déconnectez-vous de Windows et reconnectez-vous :
>
> ```powershell
> net localgroup docker-users <votre utilisateur Windows> /add
> ```

**3️⃣ make**. Dans PowerShell :

```powershell
winget install ezwinports.make
```

**4️⃣ Vérification**. D'abord, **fermez le terminal et ouvrez-en un nouveau** : les nouvelles commandes ne sont trouvées que dans un nouveau terminal. Puis :

```powershell
git --version
make --version
docker --version
docker compose version
docker run --rm hello-world
```

✅ `docker compose version` affiche la version **2** ou plus, et `hello-world` affiche *Hello from Docker!*

> ⚠️ À la [section 5](#-5-récupérer-le-dépôt), clonez le dépôt dans un dossier **non synchronisé par OneDrive** (*Documents* et *Bureau* le sont souvent), par exemple `C:\dev`.

<details>
<summary><b>🆓 Windows, alternative gratuite : WSL 2 et Docker Engine, sans Docker Desktop</b></summary>

<br>

Tout se passe alors dans **Ubuntu**, un Linux dans Windows, avec les mêmes commandes que sous Linux. Suivez ces étapes à la place des étapes 1️⃣ à 4️⃣ ci-dessus.

**1️⃣ WSL et Ubuntu**. Dans un PowerShell ouvert **en administrateur**, puis redémarrez Windows :

```powershell
wsl --install
```

Ouvrez **Ubuntu** (menu Démarrer, ou un onglet de Windows Terminal), et choisissez un nom d'utilisateur et un mot de passe Linux.

✅ Vérification dans PowerShell : `wsl --list --verbose` affiche Ubuntu avec la VERSION **2**.

**2️⃣ systemd**, qui démarre Docker.

✅ Vérification dans Ubuntu : `ps -p 1 -o comm=` affiche `systemd` (c'est le cas par défaut pour Ubuntu installé avec `wsl --install`).

Ce n'est pas le cas ? Ajoutez ces lignes à `/etc/wsl.conf` (`sudo nano /etc/wsl.conf`), lancez `wsl --shutdown` dans PowerShell, et rouvrez Ubuntu :

```ini
[boot]
systemd=true
```

**3️⃣ Git, make et Docker Engine** : dans Ubuntu, suivez la section **🐧 Linux** ci-dessous, avec ses commandes pour Ubuntu. Quand elle dit de redémarrer l'ordinateur : fermez Ubuntu, lancez `wsl --shutdown` dans PowerShell, et rouvrez Ubuntu.

> ⚠️ À la [section 5](#-5-récupérer-le-dépôt), clonez le dépôt **dans votre dossier personnel Ubuntu** (`cd ~`), pas dans `/mnt/c/...` : c'est beaucoup plus rapide. Toutes les commandes de ce guide se lancent alors dans Ubuntu.

</details>

</details>

<details>
<summary><b>🍎 macOS</b></summary>

<br>

**1️⃣ Git et make** sont fournis avec les Command Line Tools d'Apple (*déjà installés* ? très bien) :

```sh
xcode-select --install
```

Vérification :

```sh
git --version
make --version
```

**2️⃣ Docker**, l'un des deux :

- **Docker Desktop** (recommandé) : téléchargez-le sur <https://docs.docker.com/desktop/setup/install/mac-install/>, la version de votre puce (Apple ou Intel : menu Apple › À propos de ce Mac). Lancez-le, et attendez qu'il affiche *Engine running*.
- **Colima**, l'alternative gratuite, en ligne de commande uniquement : ouvrez le bloc ci-dessous.

<details>
<summary><b>🆓 macOS, alternative gratuite : Colima</b></summary>

<br>

Colima s'installe avec Homebrew : `brew --version` ne répond pas ? Installez d'abord Homebrew avec la commande de <https://brew.sh>, et suivez les *Next steps* qu'elle affiche. Ensuite :

```sh
brew install colima docker docker-compose
mkdir -p ~/.docker/cli-plugins
ln -sfn "$(brew --prefix)/opt/docker-compose/bin/docker-compose" ~/.docker/cli-plugins/docker-compose
colima start --cpu 4 --memory 6
```

> ⚠️ Colima ne démarre pas tout seul : relancez `colima start --cpu 4 --memory 6` après chaque redémarrage de votre Mac.

</details>

**3️⃣ Vérification** :

```sh
docker --version
docker compose version
docker run --rm hello-world
```

✅ `docker compose version` affiche la version **2** ou plus, et `hello-world` affiche *Hello from Docker!*

</details>

<details>
<summary><b>🐧 Linux</b></summary>

<br>

Les commandes ci-dessous sont pour **Ubuntu** (22.04 ou plus récent). Fedora : voir le bloc à la fin de cette section. Debian et les autres distributions : <https://docs.docker.com/engine/install/>, choisissez la vôtre.

> ⚠️ N'utilisez ni le *snap* de Docker, ni Docker Desktop : Docker Engine suffit.

**1️⃣ Git et make** :

```sh
sudo apt update
sudo apt install -y git make
```

Vérification :

```sh
git --version
make --version
```

**2️⃣ Docker Engine** et son plugin compose, depuis le dépôt de Docker (instructions officielles : <https://docs.docker.com/engine/install/ubuntu/>).

Retirez d'abord les paquets non officiels, s'il y en a :

```sh
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc docker-buildx podman-docker containerd runc | cut -f1)
```

Ajoutez le dépôt de Docker :

```sh
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
```

Installez Docker Engine, la commande `docker` et son plugin compose (Docker démarre alors tout seul, y compris au démarrage de l'ordinateur) :

```sh
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

**3️⃣ Docker sans sudo** : rejoignez le groupe `docker` :

```sh
sudo usermod -aG docker $USER
```

> ⚠️ Puis **redémarrez l'ordinateur** (fermer le terminal ne suffit pas) : jusque-là, Docker répond *permission denied*. Pour utiliser Docker tout de suite, dans le terminal courant uniquement : `newgrp docker`.

**4️⃣ Vérification**, sans `sudo` :

```sh
docker --version
docker compose version
docker run --rm hello-world
```

✅ `docker compose version` affiche la version **2** ou plus, et `hello-world` affiche *Hello from Docker!*

<details>
<summary><b>🐧 Linux, Fedora</b></summary>

<br>

Git et make :

```sh
sudo dnf install -y git make
```

Docker Engine (instructions officielles : <https://docs.docker.com/engine/install/fedora/>) :

```sh
sudo dnf config-manager addrepo --from-repofile https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

Puis les étapes 3️⃣ et 4️⃣ ci-dessus.

</details>

</details>

### 🔐 4. Relier Git à GitHub

Le jour J, chaque équipe pousse son travail sur sa propre branche du dépôt, pour que les organisateurs puissent le vérifier. Ils donnent le droit de pousser au compte GitHub que vous leur avez donné : préparez votre ordinateur à se connecter avec lui. Dans votre terminal (Windows : Git Bash ou PowerShell ; avec WSL : Ubuntu) :

**1️⃣ Votre identité**, inscrite dans chacun de vos commits :

```sh
git config --global user.name "Votre Nom"
git config --global user.email "vous@example.com"
```

Utilisez une adresse e-mail de votre compte GitHub (<https://github.com/settings/emails>), pour que vos commits vous soient rattachés. Votre adresse y est privée (*Keep my email addresses private*) ? Utilisez l'adresse `...@users.noreply.github.com` que cette page affiche.

✅ `git config --global user.email` affiche cette adresse.

**2️⃣ Une clé SSH**, avec laquelle Git se connecte à GitHub sans mot de passe. Vous en avez déjà une sur votre compte GitHub ? Passez à l'étape 3️⃣. Sinon, créez-la (Entrée à chaque question ; une phrase de passe est facultative) :

```sh
ssh-keygen -t ed25519 -C "vous@example.com"
```

Affichez sa partie publique :

```sh
cat ~/.ssh/id_ed25519.pub
```

> 💡 Windows affiche *'cat' n'est pas reconnu en tant que commande interne ou externe* ? Vous êtes dans une Invite de commandes (cmd), pas dans PowerShell : lancez plutôt `type %USERPROFILE%\.ssh\id_ed25519.pub`.

Copiez toute la ligne, et ajoutez-la à votre compte GitHub : <https://github.com/settings/keys> › **New SSH key**, collez-la dans *Key*, puis **Add SSH key**.

**3️⃣ Vérification** (la première fois, répondez `yes` à la question sur l'authenticité de github.com) :

```sh
ssh -T git@github.com
```

✅ Il répond *Hi \<votre utilisateur GitHub\>! You've successfully authenticated, but GitHub does not provide shell access.*, avec l'utilisateur que vous avez donné aux organisateurs.

> [!NOTE]
> Vous poussez déjà sur GitHub en HTTPS depuis cet ordinateur (GitHub CLI, Git Credential Manager...) ? Vous pouvez le garder : à la [section 5](#-5-récupérer-le-dépôt), clonez plutôt avec `https://github.com/wimar-odoo/OdooHack-LU-2026.git`.

### 📥 5. Récupérer le dépôt

Dans le dossier de votre choix :

- **Windows** : hors OneDrive, par exemple `C:\dev` ;
- **WSL** : dans Ubuntu, `cd ~`.

```sh
git clone -b 20.0-pre_hackathon_setup git@github.com:wimar-odoo/OdooHack-LU-2026.git
cd OdooHack-LU-2026
git branch --show-current
```

✅ La dernière commande affiche `20.0-pre_hackathon_setup`.

Dans le dossier :

```text
OdooHack-LU-2026/
├── Makefile             les commandes make (make help les liste)
├── docker-compose.yml   les deux conteneurs : Odoo 20 et PostgreSQL 16
├── docker/
│   ├── odoo.conf        la configuration d'Odoo
│   ├── start.sh         son démarrage
│   └── check.sh         les vérifications de make check
└── PRE-REQUISITES.md    ce guide
```

Le jour J, les modules des challenges (dossiers `trivia_*`) viendront à côté de ces fichiers.

### 🚀 6. Lancer Odoo pour la première fois

Dans le dossier du dépôt :

```sh
make check
make init
```

- **`make check`** doit répondre *Docker is ready.* Sinon, il dit quoi faire.
- **`make init`** télécharge Odoo et PostgreSQL (environ 1 Go, la première fois seulement), puis crée une base vide : *no trivia_\* module yet, creating the database* est normal. Il se termine dès qu'Odoo répond : quelques minutes la première fois.

Ensuite :

1. ouvrez <http://localhost:8069> ;
2. connectez-vous avec `admin` / `admin` ;
3. ✅ vous êtes dans Odoo, encore sans application.

**Les commandes de tous les jours**, à essayer dès maintenant :

| Commande | Quoi |
|---|---|
| `make down` | Arrêter Odoo (la base est conservée) |
| `make up` | Relancer Odoo |
| `make logs` | Suivre les logs d'Odoo (`Ctrl+C` pour quitter) |
| `make help` | Lister toutes les commandes |

> [!TIP]
> Jusqu'au hackathon, vous pouvez arrêter Odoo avec `make down`. Gardez le dossier : les téléchargements et la base serviront le jour J.

### 🔑 7. Vérifier vos accès

**GitHub** : <https://github.com/wimar-odoo/OdooHack-LU-2026> s'ouvre. Il est public : aucune invitation n'est nécessaire pour le lire, et votre `git clone` l'a déjà utilisé. Le droit de pousser arrive le jour J : GitHub envoie alors une invitation au compte que vous avez donné aux organisateurs. Acceptez-la, depuis son e-mail ou sur <https://github.com/wimar-odoo/OdooHack-LU-2026/invitations>.

**Odoo.sh** :

1. attendez l'e-mail d'invitation des organisateurs ;
2. connectez-vous sur <https://www.odoo.sh> avec votre compte GitHub (celui que vous avez donné aux organisateurs) ;
3. ouvrez <https://www.odoo.sh/project/odoo-ps-hackathon26> : ✅ vous voyez le projet.

Accès refusé, ou toujours pas d'invitation quelques jours avant le hackathon ? [Contactez-nous](#-10-nous-contacter).

### 🩹 8. Dépannage

> [!TIP]
> Lancez d'abord `make check` : il trouve la plupart des problèmes, et dit quoi faire.

Cliquez sur votre problème :

<details>
<summary><b>Windows : la virtualisation est désactivée</b> : <code>Virtualization support not detected</code>, <code>0x80370102</code></summary>

<br>

Docker Desktop et WSL 2 ont besoin de la virtualisation du processeur. Vérifiez-la dans le Gestionnaire des tâches › **Performances** › **Processeur** : *Virtualisation* doit afficher *Activé*.

Elle affiche *Désactivé* ? Activez-la dans le BIOS/UEFI de votre ordinateur (redémarrez-le, et appuyez sur la touche affichée au démarrage, souvent F2, F10, Suppr ou Échap). Selon le fabricant, l'option s'appelle *Intel Virtualization Technology* (VT-x) ou *SVM Mode* (AMD). Sur un ordinateur de votre entreprise, demandez à son service informatique.

</details>

<details>
<summary><b>Docker ne répond pas</b> : <code>Cannot connect to the Docker daemon</code>, <code>failed to connect to the docker API</code></summary>

<br>

Démarrez-le :

- **Docker Desktop** : attendez qu'il affiche *Engine running* ;
- **Colima** : `colima start --cpu 4 --memory 6` ;
- **Linux et WSL** : `sudo systemctl start docker`.

</details>

<details>
<summary><code>permission denied</code> sur <code>/var/run/docker.sock</code> (Linux, WSL)</summary>

<br>

Votre terminal ne sait pas encore que vous êtes dans le groupe `docker` :

1. Rejoignez-le (étape 3️⃣ de la section Linux ; aucun problème si c'est déjà fait) : `sudo usermod -aG docker $USER`.
2. Pour corriger tout de suite, dans le terminal courant uniquement : `newgrp docker`.
3. Pour corriger définitivement, dans tous les terminaux : Linux : redémarrez l'ordinateur (fermer le terminal ne suffit pas) ; WSL : `wsl --shutdown` dans PowerShell, puis rouvrez Ubuntu.

</details>

<details>
<summary><code>you must be in the "docker-users" group</code> (Windows, Docker Desktop)</summary>

<br>

Voir l'étape 2️⃣ de la section Windows.

</details>

<details>
<summary><code>make: command not found</code>, <code>make n'est pas reconnu</code></summary>

<br>

Installez make ([section 3](#-3-installer-les-outils)), puis ouvrez un nouveau terminal.

</details>

<details>
<summary><code>docker: 'compose' is not a docker command</code></summary>

<br>

Docker Compose version 2 manque (l'ancien `docker-compose`, version 1, ne suffit pas) :

- **Linux** : `sudo apt install docker-compose-plugin` ;
- **macOS avec Colima** : les commandes `mkdir` et `ln -sfn` de la section macOS.

</details>

<details>
<summary><code>Permission denied (publickey)</code> (Git, GitHub)</summary>

<br>

GitHub ne connaît pas la clé SSH de cet ordinateur : ajoutez-la à votre compte GitHub, voir l'étape 2️⃣ de la [section 4](#-4-relier-git-à-github), puis relancez `ssh -T git@github.com`.

</details>

<details>
<summary><code>ssh: connect to host github.com port 22</code> : <code>Connection timed out</code>, <code>Connection refused</code></summary>

<br>

Le réseau bloque SSH (port 22), comme certaines entreprises et certains Wi-Fi publics. GitHub accepte aussi SSH sur le port 443 : ajoutez ces lignes au fichier `~/.ssh/config` (créez-le si besoin), puis relancez `ssh -T git@github.com` :

```text
Host github.com
    Hostname ssh.github.com
    Port 443
    User git
```

</details>

<details>
<summary><b>Windows : Odoo est lent, ou des fichiers sont introuvables</b></summary>

<br>

Clonez le dépôt hors OneDrive (par exemple `C:\dev`), ou avec WSL dans votre dossier personnel Ubuntu, pas dans `/mnt/c`.

</details>

<details>
<summary><b>Fins de ligne</b> : <code>$'\r': command not found</code>, <code>/bin/sh^M</code>, <code>bad interpreter</code></summary>

<br>

Le dépôt garde les fins de ligne Unix, mais un outil les a converties. Supprimez le dossier et clonez-le à nouveau. Avec WSL, clonez-le dans Ubuntu : ne le copiez pas depuis Windows.

</details>

<details>
<summary><b>Odoo ne démarre pas</b>, <code>exited (137)</code></summary>

<br>

`make up` et `make init` affichent la fin des logs d'Odoo, avec l'erreur ; `make logs` les affiche tous.

*exited (137)* : Docker manque de mémoire, donnez-lui au moins 4 Go :

- **Docker Desktop** : Settings › Resources ;
- **Colima** : `colima stop`, puis `colima start --cpu 4 --memory 6`.

</details>

<details>
<summary><b>Port 8069 déjà utilisé</b> : <code>port is already allocated</code>, <code>address already in use</code></summary>

<br>

Un autre programme, peut-être un autre Odoo, l'utilise. Arrêtez-le, ou créez un fichier `.env` à côté de `docker-compose.yml` avec cette ligne :

```ini
ODOO_PORT=8070
```

Puis lancez `make up`, et ouvrez <http://localhost:8070>.

</details>

<details>
<summary><b>Conteneurs déjà présents, ou comportement étrange</b></summary>

<br>

Repartez de zéro avec `make reset` (il supprime la base locale : aucun problème avant le hackathon), puis `make init`.

</details>

<details>
<summary><b>Windows :</b> <code>make shell</code> ou <code>make psql</code> affichent <code>the input device is not a TTY</code></summary>

<br>

Lancez-les dans Windows Terminal, pas dans la fenêtre Git Bash.

</details>

### ✅ 9. Checklist finale

- [ ] `git --version`, `make --version` et `docker compose version` (2 ou plus) répondent
- [ ] `docker run --rm hello-world` affiche *Hello from Docker!*, sans `sudo`
- [ ] `git config --global user.email` affiche une adresse de votre compte GitHub, et `ssh -T git@github.com` répond *Hi \<votre utilisateur GitHub\>!*
- [ ] le dépôt est cloné, sur la branche `20.0-pre_hackathon_setup`
- [ ] `make check` répond *Docker is ready.*
- [ ] `make init` s'est terminé, et <http://localhost:8069> s'ouvre avec `admin` / `admin`
- [ ] <https://github.com/wimar-odoo/OdooHack-LU-2026> et <https://www.odoo.sh/project/odoo-ps-hackathon26> s'ouvrent
- [ ] votre éditeur de code préféré est installé

<div align="center">

**Tout est coché ? Votre ordinateur est prêt : à bientôt pour le jour J ! 🧀**

</div>

### 📬 10. Nous contacter

Un problème que ce guide ne résout pas ? Écrivez-nous, avec la commande lancée et toute sa sortie (une capture d'écran convient) :

> **William Marette**, Software Developer<br>
> ✉️ <wimar@odoo.com>
