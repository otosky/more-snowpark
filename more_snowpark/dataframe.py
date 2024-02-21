from typing import Callable

from snowflake import snowpark


def transform(self, func: Callable[[snowpark.DataFrame], snowpark.DataFrame]) -> snowpark.DataFrame:
    return func(self)


def patch():
    snowpark.DataFrame.transform = transform
