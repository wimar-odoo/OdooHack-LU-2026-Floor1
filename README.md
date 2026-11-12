# 🧀 Trivi'Hackathon 2026

[🇬🇧 English](#-english) · [🇫🇷 Français](#-français)

---

## 🇬🇧 English

An Odoo hackathon in the form of a Trivial Pursuit: 6 non-profit organisations, 6 challenges, 6 wedges to collect.

| Module | Wedge | Organisation | Topic |
|---|---|---|---|
| `trivia_hackathon` | | Trivi'Hackathon | Game engine: board, checkers |
| `trivia_food_bank` | 🔵 | Les Restos du Quartier | Functional: contacts, invoicing, CRM, email marketing |
| `trivia_reuse_center` | 🟢 | La Ressourcerie | Functional: inventory, traceability, pricelists, point of sale |
| `trivia_garden` | 🟡 | Gaart fir Jiddereen | Python: models, inheritance, computed fields, constraints, views |
| `trivia_animal_shelter` | 🟣 | Refuge Les 4 Pattes | Website: controllers, QWeb, Bootstrap, SCSS, PDF report |
| `trivia_charity_run` | 🟠 | La Course du Cœur | SQL: SQL views, window functions, performance, injection |
| `trivia_festival` | 🔴 | Festival Solidaire | JavaScript: OWL components, field widget, client action |

### How you play

- In Odoo, the app **Trivi'Hackathon** shows the board. Open a challenge: its **statement** says what to do. Click **Check**: the report says what is done and what is missing. Once all the requirements are met, the challenge is solved and its wedge goes on the board. The ⭐ are bonus.
- **Functional challenges 🔵 🟢**: on **Odoo.sh**, in the database of your team branch.
- **Development challenges 🟡 🟣 🟠 🔴**: write and test your code on **your computer**, with Docker (explore the data with `make psql` or `make shell`, not on Odoo.sh). Once it works, push it to your team branch, then click **Check** again in the Odoo of your team on Odoo.sh.
- **The board of your team on Odoo.sh counts at the end.** A push does not rebuild its database: what you did there is kept.
- **Use every tool you like**: internet, the documentation and the code of Odoo, AI...
- **Fair play**: don't change the engine `trivia_hackathon` nor the checkers (`models/trivia_challenge.py` of each module). Your commits will clearly show it if you cheat.

### Get your team branch

Docker is installed and Odoo already runs on your computer ([PRE-REQUISITES.md](PRE-REQUISITES.md#-english)). Accept the GitHub invitation that you received by e-mail, then, in the folder of the repository:

```sh
git fetch origin
git switch 20.0-hacklu26-team<n>    # <n>: the number of your team
make init                           # installs the modules of the challenges
```

Then open <http://localhost:8069> and log in with `admin` / `admin`. The Odoo of your team is on Odoo.sh: in the project of the hackathon, branch `20.0-hacklu26-team<n>`.

### Commands

| What | Command |
|---|---|
| Update the modules after a change | `make update` |
| Start / stop Odoo | `make up` / `make down` |
| Start Odoo with debugging tools ([`pdb`](https://docs.python.org/3/library/pdb.html)/[`ipdb`](https://pypi.org/project/ipdb/)/[`pudb`](https://documen.tician.de/pudb/starting.html#starting-the-debugger)) | `make debug` |
| Follow the logs (your errors are there!) | `make logs` |
| Odoo shell | `make shell` |
| PostgreSQL console | `make psql` |
| Start over: deletes the local database! | `make reset`, then `make init` |
| Check Docker | `make check` |

### Good to know

- Changed an **existing view**, **JavaScript** or an **OWL template**? Reloading the page is enough.
- Changed **Python code**, added a **field**, a **model**, a **file** or a **record**? Update the modules (`make update`, all of them at once), and don't forget to declare the new files in `__manifest__.py`.
- <http://localhost:8069> does not answer? Odoo stops when the installation or an update fails: `make logs` shows why. Fix, then `make update`.
- A problem with Docker? `make check` says what to do, and [PRE-REQUISITES.md](PRE-REQUISITES.md#-8-troubleshooting) lists the usual cases.
- **Push only to your team branch**: everyone can push to every team branch, so check `git branch --show-current` before `git push`.
- `git push` refused (`Permission denied`, `403`)? Accept the GitHub invitation. Refused because your team pushed first? `git pull --rebase`, then `git push`.
- `git push --force` refused? On purpose.

---

## 🇫🇷 Français

Un hackathon Odoo en forme de Trivial Pursuit : 6 ASBL, 6 challenges, 6 parts de camembert à collectionner.

| Module | Part | ASBL | Thème |
|---|---|---|---|
| `trivia_hackathon` | | Trivi'Hackathon | Moteur du jeu : plateau, checkers |
| `trivia_food_bank` | 🔵 | Les Restos du Quartier | Fonctionnel : contacts, facturation, CRM, marketing par e-mail |
| `trivia_reuse_center` | 🟢 | La Ressourcerie | Fonctionnel : inventaire, traçabilité, listes de prix, point de vente |
| `trivia_garden` | 🟡 | Gaart fir Jiddereen | Python : modèles, héritage, champs calculés, contraintes, vues |
| `trivia_animal_shelter` | 🟣 | Refuge Les 4 Pattes | Site web : contrôleurs, QWeb, Bootstrap, SCSS, rapport PDF |
| `trivia_charity_run` | 🟠 | La Course du Cœur | SQL : vues SQL, fonctions de fenêtre, performance, injection |
| `trivia_festival` | 🔴 | Festival Solidaire | JavaScript : composants OWL, widget de champ, action client |

### Comment jouer

- Dans Odoo, l'application **Trivi'Hackathon** affiche le plateau. Ouvrez un challenge : son **énoncé** dit quoi faire. Cliquez sur **Vérifier** : le rapport dit ce qui est fait et ce qui manque. Une fois toutes les exigences remplies, le challenge est résolu et sa part va sur le plateau. Les ⭐ sont des bonus.
- **Challenges fonctionnels 🔵 🟢** : sur **Odoo.sh**, dans la base de la branche de votre équipe.
- **Challenges de développement 🟡 🟣 🟠 🔴** : écrivez et testez votre code sur **votre ordinateur**, avec Docker (explorez les données avec `make psql` ou `make shell`, pas sur Odoo.sh). Une fois qu'il fonctionne, poussez-le sur la branche de votre équipe, puis cliquez à nouveau sur **Vérifier** dans l'Odoo de votre équipe sur Odoo.sh.
- **C'est le plateau de votre équipe sur Odoo.sh qui compte à la fin.** Un push ne reconstruit pas sa base : ce que vous y avez fait est conservé.
- **Utilisez tous les outils que vous voulez** : internet, la documentation et le code d'Odoo, l'IA…
- **Fair-play** : ne modifiez ni le moteur `trivia_hackathon` ni les checkers (`models/trivia_challenge.py` de chaque module). Vos commits montreront clairement si vous trichez.

### Récupérer la branche de votre équipe

Docker est installé et Odoo tourne déjà sur votre ordinateur ([PRE-REQUISITES.md](PRE-REQUISITES.md#-français)). Acceptez l'invitation GitHub reçue par e-mail, puis, dans le dossier du dépôt :

```sh
git fetch origin
git switch 20.0-hacklu26-team<n>    # <n> : le numéro de votre équipe
make init                           # installe les modules des challenges
```

Ouvrez ensuite <http://localhost:8069> et connectez-vous avec `admin` / `admin`. L'Odoo de votre équipe est sur Odoo.sh : dans le projet du hackathon, branche `20.0-hacklu26-team<n>`.

### Commandes

| Quoi | Commande |
|---|---|
| Mettre à jour les modules après une modification | `make update` |
| Démarrer / arrêter Odoo | `make up` / `make down` |
| Démarrer Odoo avec les outils de débogage ([`pdb`](https://docs.python.org/3/library/pdb.html)/[`ipdb`](https://pypi.org/project/ipdb/)/[`pudb`](https://documen.tician.de/pudb/starting.html#starting-the-debugger)) | `make debug` |
| Suivre les logs (vos erreurs sont là !) | `make logs` |
| Shell Odoo | `make shell` |
| Console PostgreSQL | `make psql` |
| Repartir de zéro : supprime la base locale ! | `make reset`, puis `make init` |
| Vérifier Docker | `make check` |

### Bon à savoir

- Vous avez modifié une **vue existante**, du **JavaScript** ou un **template OWL** ? Recharger la page suffit.
- Vous avez modifié du **code Python**, ajouté un **champ**, un **modèle**, un **fichier** ou un **enregistrement** ? Mettez les modules à jour (`make update`, tous en une fois), sans oublier de déclarer les nouveaux fichiers dans `__manifest__.py`.
- <http://localhost:8069> ne répond pas ? Odoo s'arrête quand l'installation ou une mise à jour échoue : `make logs` dit pourquoi. Corrigez, puis `make update`.
- Un problème avec Docker ? `make check` dit quoi faire, et [PRE-REQUISITES.md](PRE-REQUISITES.md#-8-dépannage) liste les cas habituels.
- **Ne poussez que sur la branche de votre équipe** : tout le monde peut pousser sur toutes les branches d'équipe, donc vérifiez `git branch --show-current` avant `git push`.
- `git push` refusé (`Permission denied`, `403`) ? Acceptez l'invitation GitHub. Refusé parce que votre équipe a poussé avant vous ? `git pull --rebase`, puis `git push`.
- `git push --force` refusé ? C'est voulu.
