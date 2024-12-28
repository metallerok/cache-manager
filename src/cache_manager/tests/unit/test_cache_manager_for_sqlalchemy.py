import uuid
from cache_manager.main import CacheManager
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.cache_manager.tests.helpers import (
    Base,
    Task,
    Sprint,
)


def test_sqlaclhemy_models_caching(postgres_fx, redis_fx):
    db_uri = postgres_fx

    engine = create_engine(db_uri)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db_session = sessionmaker(
        engine, expire_on_commit=False
    )()

    sprint = Sprint(
        id=uuid.uuid4(),
        title="sprint"
    )
    db_session.add(sprint)

    task1 = Task(
        id=uuid.uuid4(),
        title="task 1",
        sprint=sprint

    )
    db_session.add(task1)
    task1_id = task1.id

    task2 = Task(
        id=uuid.uuid4(),
        title="task 2",
        sprint=sprint

    )
    db_session.add(task2)

    db_session.commit()

    tasks_cache_manager = CacheManager(
        redis=redis_fx,
        model_version=Task.__model_version__,
        prefix=Task.__tablename__
    )

    tasks_cache_manager.set(obj=task1, obj_id=task1.id, ttl=60)

    task: Task = tasks_cache_manager.get(obj_id=task1.id, model_class=Task)

    assert task
    assert task.id == task1_id
    assert task.sprint.id == sprint.id
    assert task.sprint.title == sprint.title
