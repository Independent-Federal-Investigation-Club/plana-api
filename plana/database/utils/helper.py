import os
from snowflake import SnowflakeGenerator

SNOWFLAKE_GEN = SnowflakeGenerator(hash(os.uname().nodename) % 1024)
