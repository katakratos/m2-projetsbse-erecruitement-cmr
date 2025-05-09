import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from logging.config import fileConfig

from alembic import context
from app.services.database import Base, engine

# Ajoutez le chemin de votre projet au PYTHONPATH

# Chargement de la configuration
config = context.config

# Configuration du logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# IMPORTANT: Chargez vos modèles de manière explicite
# plutôt que dynamiquement pour éviter les problèmes

target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
