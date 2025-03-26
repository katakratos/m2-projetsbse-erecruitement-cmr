# eRecrutement

This a backenk of eRecrutment APP

## Table of contents
- [eRecrutement](#erecrutement)

    - [Table of contents](#table-of-contents)
    -[Prerequisites](#prerequisites)
    -[I. Installation and configuration]
     (#i-installation-and-configuration)

## Prerequisites

Before to get started these are the tools that you need.

[x] Python 3.11+ (Complete with a [link](https://www.python.org/) related to the installation)

[x] Poetry 1.4+ (Complete with a [link](https://python-poetry.org/) related to the installation)

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
#### I.1.1. Base installation

Install python dependencies

```sh
poetry install --all-extras
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