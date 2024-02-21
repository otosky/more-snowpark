from typing import Callable
from typing import Sequence
from typing import Tuple

from snowflake import snowpark
from snowflake.snowpark import functions as F
from snowflake.snowpark import types as T


def transform(self: snowpark.DataFrame, func: Callable[[snowpark.DataFrame], snowpark.DataFrame]) -> snowpark.DataFrame:
    return func(self)


def _schema_diff(s1, s2) -> Tuple[Sequence[T.StructField], Sequence[T.StructField], Sequence[T.StructField]]:
    intersection = []
    missing_in_s1 = []
    missing_in_s2 = []

    for f in s1.fields:
        if f not in s2.fields:
            missing_in_s2.append(f)
        else:
            intersection.append(f)

    for f in s2.fields:
        if f not in s1.fields:
            missing_in_s1.append(f)

    return missing_in_s1, intersection, missing_in_s2


def _add_missing_columns(df: snowpark.DataFrame, missing_columns: Sequence[T.StructField]) -> snowpark.DataFrame:
    null_columns = {field.name: F.lit(None).cast(field.datatype) for field in missing_columns}
    return df.with_columns(null_columns.keys(), null_columns.values())  # type:ignore


def _union_all_by_name(self: snowpark.DataFrame, other: snowpark.DataFrame) -> snowpark.DataFrame:
    missing_from_self, _, missing_from_other = _schema_diff(self.schema, other.schema)

    new_self = _add_missing_columns(self, missing_from_self)
    new_other = _add_missing_columns(other, missing_from_other)

    return new_self.union_all_by_name(new_other)


def patch():
    snowpark.DataFrame.transform = transform
    snowpark.DataFrame._union_all_by_name = _union_all_by_name
