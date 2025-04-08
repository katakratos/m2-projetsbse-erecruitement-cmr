# eRecrutement

This a backenk of eRecrutment APP

## Table of contents

- [eRecrutement](#erecrutement)

  - [Table of contents](#table-of-contents) -[Prerequisites](#prerequisites) -[I. Installation and configuration]
    (#i-installation-and-configuration)

## Prerequisites

Before to get started these are the tools that you need.

[x] Python 3.10+ (Complete with a [link](https://www.python.org/) related to the installation)

[x] Poetry 1.8+ (Complete with a [link](https://python-poetry.org/) related to the installation)

[x] VS Code (Complete with a [link](https://code.visualstudio.com/) related to the installation)

[ ] Docker (Complete with a [link](https://www.docker.com/) related to the installation)

[ ] sqlite3 (Complete with a [link](https://www.sqlite.org/) related to the installation)

## I. Installation and configuration

### I.1. Development environment

Clone the project

```sh
git clone https://github.com/m2_projetsbse-erecruitement-cmr/m2_projetsbse-erecruitement-cmr.git
```

Move to workdir

```sh
cd m2_projetsbse-erecruitement-cmr/
```

Refer to **.env.example** file to create your own **.env** file to configurate Nzhinu-Farm App

> **_ATTENTION_** The app need specifics variables environments to launch, refer to .env.example file

#### I.1.1. Base installation

Install python dependencies

```sh
poetry install --all-extras
```

Apres installation des packages s'il y a erreur taper cette commande et poetry se chargera de resoudre le probleme de file/folder inexistantes

```sh
poetry lock --no-update
```

Active virtual environment

```sh
poetry shell
```

Run Public App

```sh
poetry run uvicorn app.main:app --reload
```

Utilise pour les migrations

```sh
alembic revision --autogenerate -m "Initial migration"
```

```sh
alembic upgrade head
```

Commannde pour supprimer les données de la base de données et la recréer

```sh
rm your_database.db # Supprime la base de données
rm -rf alembic/version/* # Supprime tous les fichiers de migrations existantes
alembic downgrade base
alembic revision --autogenerate -m "nom_de_opération_effectuée" # Détecte les migrations, il faut spécifier le noms de l'opération effectuée
alembic upgrade head
```
