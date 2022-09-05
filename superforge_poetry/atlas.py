# superforge_poetry/atlas.py

from datetime import datetime
from enum import Enum, unique
from os import environ
from pathlib import Path
from typing import Optional

import motor.motor_asyncio
from beanie import Document, Indexed, init_beanie
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import (UUID4, AnyUrl, BaseModel, DirectoryPath, Field, FilePath,
                      HttpUrl, conint)
from pymongo import ASCENDING, DESCENDING
from rich import inspect, print
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

try:
    from log import BASE, log, max_console
except ModuleNotFoundError as ModNotFound:
    from superforge_poetry.log import BASE, log, max_console
except ImportError as ImportError:
    from superforge_poetry.log import BASE, log, max_console

load_dotenv("env/.env")


class InvalidDatabase(ValueError):
    """Custom exception for invalid database."""
    pass


class Chapter(Document):
    """This class contains the chapter content and metadata."""

    chapter: int = Field(
        gt=0,
        le=3462,
        unique_items=True,
        description="The chapter number.",)
    section: int = Field(
        gt=0,
        le=17,
        description="The section number.",)
    book: int = Field(
        gt=0,
        le=10,
        description="The book number.",)
    title: str = Field(..., description="The given chapter's title.")
    text: str = Field(..., description="The given chapter's text.")
    filename: str = Field(..., description="The given chapter's filename.")
    md_path: FilePath = Field(..., description="The filepath to chapter's markdown.")
    html_path: FilePath = Field(..., description="The filepath to chapter's markdown.")
    md: str = Field(..., description="The given chapter's markdown.")
    html: str = Field(..., description="The given chapter's html.")
    url: HttpUrl
    unparsed_text: str
    parsed_text: str
    meta = {
        "abstract": True
    },
    class Settings:
        name = "chapter",
        indexes = [
            "chapter",
            [
                ("chapter", ASCENDING),
            ]
        ],
        validate_on_save = True,

    def to_json(self):
        """Return the chapter as a json string."""
        return {
            "chapter": self.chapter,
            "section": self.section,
            "book": self.book,
            "title": self.title,
            "text": self.text,
            "filename": self.filename,
            "md_path": self.md_path,
            "html_path": self.html_path,
            "md": self.md,
            "html": self.html,
            "url": self.url,
            "unparsed_text": self.unparsed_text,
            "parsed_text": self.parsed_text,
        }


def validate_db(database: str) -> str | None:
    """
    Validate the database.
    """
    match database:
        case "LOCALDB":
            uri = AnyUrl.build(
                scheme="mongodb",
                host=str(environ.get("LOCALDB_HOST")),
                port=str(environ.get("LOCALDB_PORT")),
                db=str(environ.get("LOCALDB_DB")),
            )
            return uri
        case "SUPERGENE":
            uri = AnyUrl.build(
                scheme="mongodb",
                user=str(environ.get("SUPERGENE_USER")),
                password=str(environ.get("SUPERGENE_PASS")),
                host=str(environ.get("SUPERGENE_HOST")),
                db=str(environ.get("SUPERGENE_DB")),
            )
            return uri
        case _:
            uri = AnyUrl.build(
                scheme="mongodb",
                host=str(environ.get("LOCALDB_HOST")),
                port=str(environ.get("LOCALDB_PORT")),
                db=str(environ.get("LOCALDB_DB")),
            )
            return uri

async def init(database: str = "LOCALDB"):
    """
    Initialize the database.
    """
    URI = validate_db(database)
    client = motor.motor_asyncio.AsyncIOMotorClient(URI)
    await init_beanie(database="SUPERGENE", document_models=["Chapter"])
    return client


async def get_chapters() -> list[Chapter]:
    """
    Get all chapters from the database.
    """
    chapters = await Chapter.find_all().to_list()
    return chapters


async def get_chapter( chapter: int):
    """
    Get a chapter from the database.
    """
    doc = await Chapter.find_one(Chapter.chapter == chapter)
    return doc

async def get_chapter_text(chapter: int) -> FindOne[Chapter]:
    """
    Get a chapter's text from the database.
    """
    doc = await Chapter.find_one(Chapter.chapter == chapter)
    if doc:
        return doc.text
