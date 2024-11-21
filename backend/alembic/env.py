import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_path = Path(__file__).parent.parent
sys.path.append(str(current_path))

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.core.config import settings
from app.db.models import Base

# 获取alembic配置
config = context.config

# 设置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置目标元数据
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """离线运行迁移"""
    url = settings.get_database_url(async_url=False)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """在线运行迁移"""
    # 这里直接从配置中获取数据库URL
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.get_database_url(async_url=False)
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
