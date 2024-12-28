import pytest_asyncio
import pytest
import redis
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


@pytest.fixture(scope="session")
def postgres_fx():
    with PostgresContainer("postgres:16", password="test", dbname="test") as postgres:
        pg_url = postgres.get_connection_url()

        yield pg_url


@pytest.fixture(scope="module")
def db_session_fx(db_engine_fx):
    session = sessionmaker(
        db_engine_fx, expire_on_commit=False
    )()

    yield session

    session.close()


@pytest.fixture()
def redis_fx():
    with RedisContainer("redis:7.4.1") as redis_container:
        redis_client = redis_container.get_client()

        yield redis_client
