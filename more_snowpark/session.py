from contextlib import contextmanager

from snowflake import snowpark


@contextmanager
def transaction(session: snowpark.Session):
    session.sql("BEGIN").collect()
    try:
        yield session
        session.sql("COMMIT").collect()
    except Exception:
        session.sql("ROLLBACK").collect()
        raise
