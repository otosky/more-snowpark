from snowflake import snowpark
from snowflake.snowpark import Row
from snowflake.snowpark import functions as F


def test_transform(snowpark_session):

    def with_times2(df: snowpark.DataFrame) -> snowpark.DataFrame:
        return df.withColumn("col2", F.col("col1") * 2)

    def with_summed(df: snowpark.DataFrame) -> snowpark.DataFrame:
        return df.withColumn("col3", F.col("col1") + F.col("col2"))

    df = snowpark_session.range(1, 5, 1).to_df("col1").transform(with_times2).transform(with_summed)

    expected_rows = [
        Row(COL1=1, COL2=2, COL3=3),
        Row(COL1=2, COL2=4, COL3=6),
        Row(COL1=3, COL2=6, COL3=9),
        Row(COL1=4, COL2=8, COL3=12),
    ]

    for actual, expected in zip(df.collect(), expected_rows):
        assert actual == expected


def test_union_by_name(snowpark_session):
    df1 = snowpark_session.create_dataframe([[1]], schema=["a"])
    df2 = snowpark_session.create_dataframe([[2]], schema=["b"])
    unioned = df1._union_all_by_name(df2)

    expected_df = snowpark_session.create_dataframe([[1, None], [None, 2]], schema=["a", "b"])
    for actual, expected in zip(unioned.collect(), expected_df.collect()):
        assert actual == expected
