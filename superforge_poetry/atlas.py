# superforge_poetry/atlas.py

from typing import Optional
from pydantic import BaseModel
from beanie import Document, Indexed, init_beanie
import motor.motor_asyncio
from rich import *
from dotenv import load_dotenv
from os import environ

try:
    from log import BASE, log, max_console
except ModuleNotFoundError as ModNotFound:
    from superforge_poetry.log import BASE, log, max_console
except ImportError as ImportError:
    from superforge_poetry.log import BASE, log, max_console

load_dotenv("../env/.env")


class InvalidDatabase(ValueError):
    """Custom exception for invalid database."""

    pass


def validate_db(database: str) -> str:
    """
    Validate the database.
    """
    match database:
        case "LOCALDB":
            URI = environ.get("LOCALDB")
        case "SUPERGENE":
            URI = environ.get("SUPERGENE")
        case "MAKE_SUPERGENE":
            URI = environ.get("MAKE_SUPERGENE")
        case _:
            raise InvalidDatabase(f"{database} is not a valid database.")


async def init(database: str):
    """
    Initialize the database.
    """
    URI = validate_db(database)
    client = motor.motor_asyncio.AsyncIOMotorClient()
    db = client.get_database(URI)
    return db
