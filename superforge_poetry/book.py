# superforge_poetry/book.py

import pymongo
from typing import Optional

from pydantic import BaseModel

from beanie import Document, Link
from beanie import Indexed
from uuid import uuid4 as uuid

try:
    from log import BASE, log, max_console
except ModuleNotFoundError as ModNotFound:
    from superforge_poetry.log import BASE, log, max_console
except ImportError as ImportError:
    from superforge_poetry.log import BASE, log, max_console

# >┌─────────────────────────────────────────────────────────────────┐< #
# >│                              Book                               │< #
# >└─────────────────────────────────────────────────────────────────┘< #

class Book(Document):
    """
    Book model.
    """
    book: Indexed(int, pymongo.ASCENDING)
    title: str
    output: str
    cover: str
    cover_path: str
    uuid: str
    sections: int | list[int]
    book_word: str

    class Settings:
        name = "book"

class Section(Document):
    """
    Section model.
    """
    section: int
    title: str
    book: Link[Book]