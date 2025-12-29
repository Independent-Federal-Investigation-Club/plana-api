import asyncio
import os

from dotenv import load_dotenv

from plana.database import PlanaDB
from plana.database.models.message import Messages


async def main():
    load_dotenv()
    PlanaDB.init_db(os.getenv("DATABASE_URL"))

    # Example message ID to fetch
    message_id = "d4fcfc03-f698-46c4-a435-fce94d4c50a9"

    try:
        # Fetch the message by ID
        message = await Messages.get(message_id)
        print(f"Message fetched: {message.to_dict()}")
    except Exception as e:
        print(f"Error fetching message: {e}")


if __name__ == "__main__":
    asyncio.run(main())
