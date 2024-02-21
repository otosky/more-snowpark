import pytest
from snowflake import snowpark

from more_snowpark import patch
from more_snowpark.config import Settings


@pytest.fixture
def snowpark_session():
    patch()
    settings = Settings()
    return snowpark.Session.builder.configs(options=settings.snowflake_config).create()
