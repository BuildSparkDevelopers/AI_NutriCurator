from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Base metadata 가져오기 (모델이 많아도 __init__.py에서 import만 해주면 됨)
from domain.models import Base  
from app.settings import settings  

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _sync_database_url() -> str:
    """
        Alembic은 sync 드라이버(psycopg)를 사용해서 migration을 실행해야 함.
        하지만 애플리케이션에서는 async 드라이버(asyncpg)를 사용하기 때문에, Alembic이 사용할 URL을 변환해주는 함수입니다. 
    """
    url = settings.DATABASE_URL

    # 예: postgresql+asyncpg://...  -> postgresql+psycopg://...
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
    return url


def run_migrations_offline() -> None:
    url = _sync_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _sync_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True, 
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()