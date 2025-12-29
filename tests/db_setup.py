import asyncio
from plana.database import PlanaDB
from plana.database.utils.db import get_database_url


async def setup():

    connection_string = get_database_url()
    print(f"Using connection string: {connection_string}")
    PlanaDB.init_db(connection_string=connection_string)

    try:
        await PlanaDB.recreate_all()
    except Exception as e:
        print(f"Error initializing database: {e}")
    else:
        print("Database initialized successfully!")


asyncio.run(setup())
