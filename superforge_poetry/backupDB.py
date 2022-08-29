#! /Users/maxludden/dev/venvs/superforge/bin/python

import os
from datetime import datetime
from functools import wraps
from json import dump, load
from pathlib import Path
from time import perf_counter
import requests
from typing import Optional
import time


import mongoengine as me
from sh import mongoexport, cd, mongodump, mongorestore
from dotenv import load_dotenv
from loguru import logger
from mongoengine.fields import (
    DateTimeField,
    DictField,
    IntField,
    ListField,
    StringField,
    URLField,
    UUIDField,
)
from tqdm.auto import tqdm
from alive_progress import alive_bar, alive_it
from platform import platform
from pymongo import MongoClient
import requests

from core.yay import finished
from core.base import BASE

load_dotenv()


def generate_base():
    if platform() == "Linux":
        ROOT = "home"
    else:
        ROOT = "Users"  # < Mac
    BASE = f"/{ROOT}/maxludden/dev/py/superforge"
    return BASE


BASE = ""
BASE = generate_base()

# > Logging
RUN_PATH = f"{BASE}/json/run.json"
LOG_DIR = "logs/"
MAIN_LOG = "logs.log.md"
LOGGING_LOG = "logs/logging.log"


def get_last_run():
    """Retrieves the last run.

    Returns:
        `last_run` (int):
            The last run
    """
    with open(RUN_PATH, "r") as infile:
        last_run_dict = dict((load(infile)))

    return int(last_run_dict["last_run"])


def increment_run():
    """Increments last_run to get the current run.

    Args:
        `run` (int):
            last_run

    Returns:
        `run` (int)
            The current run.
    """
    last_run = get_last_run()
    return last_run + 1


def get_run():
    """Retrieves the current run.

    Returns:
        `run` (int):
            The current run.
    """
    return increment_run()


def write_run(run: Optional[int]):
    """Writes the current run to json file.

    Args:
        `run` (Optional[int]):
            If provided, writes the inputted int as the current run.
    """
    if not run:
        run = increment_run()
    run_dict = {"last_run": run}
    with open(RUN_PATH, "w") as outfile:
        dump(run_dict, outfile, indent=4)


def console_fmt(record: dict):
    """
    Generates the format to be used when logging stdout/stderr to the console via 'tqdm.write(msg, end="")'

    Args:
        record (dict):
            A python dict that contains the metadata of the logged message.

    Returns:
        record (dict):
            An updated python dict that contains the metadata of the logged message.
    """

    if record["exception"]:
        return """\n<lvl>  {time:h:m:ss.SSS A}  <v>  {level.name: >56}  </v>
┌───────────────┬──────────────┬──────────────────────┬───────────────────────┐
│  <u><i>SUPERFORGE</i></u>   │</lvl>    <w>Run {extra[run]: <5}</w> <lvl>│</lvl> <e>{file.name: ^21}</e><lvl>│ <m>      Line {line: <7} </m>   │
├───────────────┴──────────────┴──────────────────────┴───────────────────────┤
│<v>    𥉉  </v>   EXCEPTION    <v>   𥉉    EXCEPTION    𥉉   </v>   EXCEPTION    <v>    𥉉   </v> │
└─────────────────────────────────────────────────────────────────────────────┘
{exception}</lvl>
"""
    else:
        return """\n<lvl>  {time:h:m:ss.SSS A}  <v>  {level.name: >56}  </v>
┌───────────────┬──────────────┬──────────────────────┬───────────────────────┐
│  <u><i>SUPERFORGE</i></u>   │</lvl>    <w>Run {extra[run]: <5}</w> <lvl>│</lvl> <e>{file.name: ^21}</e><lvl>│ <m>      Line {line: <7} </m>   │
└───────────────┴──────────────┴──────────────────────┴───────────────────────┘
{message}</lvl>
"""


def console_error_flt(record: dict):
    """
    A filtering function that returns messages intended to be displayed on the console via stderr.

    Args:
        'record' (dict):
            A python dict that contains the metadata of the logged message.

    Returns:
        `record`(dict)
            An updated python dict that contains the a of the logged exception.
    """

    lvl = record["level"].no
    if lvl >= 40:
        return record


def console_info_flt(record: dict):
    """
    A filtering function that returns messages intended to be displayed on the console via stdout.

    Args:
        'record' (dict):
            A python dict that contains the metadata of the logged message.

    Returns:
        `record`(dict)
            An updated python dict that contains the metadata of the logged message.
    """
    lvl = record["level"].name
    if lvl == "INFO":
        return record
    elif lvl == "WARNING":
        return record


def console_debug_flt(record: dict):
    """
    A filtering function that returns messages intended to be displayed on the console via stdout.

    Args:
        'record' (dict):
            A python dict that contains the metadata of the logged message.

    Returns:
        `record`(dict)
            An updated python dict that contains the metadata of the logged message.
    """
    lvl = record["level"].name
    if lvl == "DEBUG":
        return record
    elif lvl == "INFO":
        return record
    elif lvl == "WARNING":
        return record


def truncate_filenames(record):
    """
    Truncate exceedingly long filenames to maintain formatting.

    Args:
        `record` (dict):
            The record dictionary of a logged message.

    Returns:
        `record` (dict):
            The edited record dictionary of the given message.
    """
    filename = record["file"].name
    if "ipython" in filename:
        filename = "ipython"
    if len(filename) > 20:
        filename = filename[0:17]
    record["file"].name = filename
    return record


current_run = get_run()
write_run(current_run)
log = logger.patch(truncate_filenames)
log.remove()  # removes the default logger provided by loguru
sinks = {}
log.configure(
    handlers=[
        dict(
            sink=(lambda msg: tqdm.write(msg, end="")),
            colorize=True,
            format=console_fmt,
            level="ERROR",
            backtrace=True,
            diagnose=True,
            catch=True,
            filter=console_error_flt,
        ),
        dict(
            sink=lambda msg: tqdm.write(msg, end=""),
            colorize=True,
            format=console_fmt,
            level="DEBUG",
            backtrace=True,
            diagnose=True,
            filter=console_debug_flt,
        ),
        dict(
            sink=f"{BASE}/logs/supergene.log",
            colorize=False,
            format="Run {extra[run]} | {time:hh:mm:ss:SSS A} | {file.name: ^13} |  Line {line: ^5} | {level: <8}ﰲ  {message}",
            level="DEBUG",
            backtrace=True,
            diagnose=True,
        ),
    ],
    extra={"run": current_run, "function": ""},
)


def md_fmt(record: dict):
    """
    A formatting function that returns the format for writing responsive logs to a markdown file.

    Note: For this function to work, at the end of a run of a script the function 'endrun()' must be called.
    """

    lvl = str(record["level"].name).lower()
    if lvl == "debug":
        return """
\<br>
\<a class="debug" href="vscode://file/{file.path}:{line}:1">
    \<div class="card-debug">
        \<div class="header-debug">
            Run {extra[run]} | {time:h:mm:ss A} | {file.name} | Line {line}
        \</div>
        \<div class="container-debug">
            \<pre>
{message}
            \</pre>
        \</div>
    \</div>
\</a>
"""
    elif lvl == "info":
        return """
\<br>
\<a class="info" href="vscode://file/{file.path}:{line}:1">
    \<div class="card-info">
        \<div class="header-info">
            Run {extra[run]} | {time:h:mm:ss A} | {file.name} | Line {line}
        \</div>
        \<div class="container-info">
            \<pre>
{message}
            \</pre>
        \</div>
    \</div>
\</a>
"""
    elif lvl == "warning":
        return """
\<br>
\<a class="warn" href="vscode://file/{file.path}:{line}:1">
    \<div class="card-warn">
        \<div class="header-warn">
            Run {extra[run]} | {time:h:mm:ss A} | {file.name} | Line {line}
        \</div>
        \<div class="container-warn">
            \<pre>
{message}
            \</pre>
        \</div>
    \</div>
\</a>
"""
    elif lvl == "error":
        return """
\<br>
\<a class="error" href="vscode://file/{file.path}:{line}:1">
    \<div class="card-error">
        \<div class="header-error">
            Run {extra[run]} | {time:h:mm:ss A} | {file.name} | Line {line}
        \</div>
        \<div class="container-error">
            \<pre>
{message}
            \</pre>
        \</div>
    \</div>
\</a>
"""


def main_flt(record: dict):
    filename = record["file"].name
    if filename != "log.py'":
        return record


def pwrap(line: str):
    return f"<p>{line}</p>"


def multiline(record):
    return str(record.message).strip()


logger = log.bind(scope="main")
logger.add(
    sink=f"{BASE}/logs/log.md",
    colorize=False,
    level="DEBUG",
    format=md_fmt,
    filter=main_flt,
    rotation="100 MB",
)
logger.patch(multiline)

# > Connecting to the database
def sg(database: str):
    """Custom mongoengine connection"""
    databases = ["SUPERGENE", "LOCALDB", "MAKE_SUPERGENE"]
    if database not in databases:
        raise ValueError(f"Database {database} not in {databases}")
    match database:
        case "SUPERGENE":
            URI = os.environ.get("SUPERGENE")
        case "LOCALDB":
            URI = os.environ.get("LOCALDB")
        case "MAKE_SUPERGENE":
            URI = os.environ.get("MAKE_SUPERGENE")
        case _:
            URI = os.environ.get("LOCALDB")
    try:
        me.connect("SUPERGENE", host=URI)
        log.debug(f"Connected to {database}")
    except ConnectionError as ce:
        log.error(f"Could not connect to {database}")
        raise ce


# > Collections
collections = [
    "Book",
    "ChapterNotFound",
    "Chapter",
    "chapter_gen",
    "Coverpage",
    "Defaultdoc",
    "EndOfBook",
    "EndOfBook",
    "Epubmeta",
    "Metadata",
    "Section",
    "Titlepage",
]


class Book(me.Document):
    """
    A book is a collection of chapters.
    """

    title = StringField(required=True, max_length=500)
    output = StringField()
    cover = StringField()
    cover_path = StringField()
    uuid = UUIDField(binary=False)
    default = StringField()
    start = IntField(min_value=1)
    end = IntField(max_value=3463)
    book = IntField()
    book_word = StringField(required=True)


class ChapterNotFound(Exception):
    pass


class Chapter(me.Document):
    chapter = IntField(required=True, unique=True)
    section = IntField()
    book = IntField(min_value=1, max_value=10, required=True)
    title = StringField(max_length=500, required=True)
    text = StringField()
    filename = StringField()
    md_path = StringField()
    html_path = StringField()
    md = StringField()
    html = StringField()
    url = URLField()
    unparsed_text = StringField()
    parsed_text = StringField()

    def __repr__(self):
        yaml_doc = f"---\nChapter: {self.chapter}\nSection: {self.section}\nBook {self.book}\nTitle: {self.title}\nFilename: {self.filename}\nMD Path: {self.md_path}\nHTML Path: {self.html_path}\n..."
        md = "\n# Chapter {self.chapter} Markdown\n  \n{self.md}\n  "
        text = f"\n \nText:\n  \n{self.text}\n"
        html = f"\n \nHTML:\n  \n{self.html}"
        return f"\n \n{yaml_doc}{md}{text}{html}"


class chapter_gen:
    """
    Generator for chapter_numbers.
    """

    def __init__(self, start: int = 1, end: int = 3462):
        self.start = start
        self.end = end
        self.chapter_number = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.chapter_number >= 3462:
            raise StopIteration
        elif self.chapter_number == 3094:
            # Skipping chapter 3095
            # 3094 + 1 + 1 = 3096
            self.chapter_number += 2
            return self.chapter_number
        elif self.chapter_number == 3116:
            # Skipping chapter 3117
            # 3116 + 1 + 1 = 3118
            self.chapter_number += 2
            return self.chapter_number
        else:
            self.chapter_number += 1
            return self.chapter_number


class Coverpage(me.Document):
    book = IntField()
    filename = StringField()
    filepath = StringField()
    html_path = StringField()
    html = StringField()
    meta = {"collection": "coverpage"}


class Defaultdoc(me.Document):
    book = IntField(unique=True, min_value=1, max_value=10)
    book_word = StringField()
    cover = StringField()
    cover_path = StringField()
    default = StringField()
    filename = StringField()
    filepath = StringField()
    input_files = ListField(StringField())
    output = StringField()
    resource_paths = ListField(StringField())
    section1_files = ListField(StringField())
    section2_files = ListField(StringField())
    section_count = IntField(min_value=1, max_value=2)
    sections = ListField(IntField(min_value=1, max_value=17))
    epubmetadata = StringField()
    metadata = StringField()
    default_doc = StringField()
    title = StringField()
    meta = {"collection": "defaultdoc"}


class EndOfBook(me.Document):
    book = IntField(Required=True, unique=True)
    book_word = StringField()
    title = StringField(Required=True, max_length=500)
    text = StringField()
    filename = StringField()
    mmd_path = StringField()
    html_path = StringField()
    mmd = StringField()
    html = StringField()
    meta = {"collection": "endofbook"}


class Epubmeta(me.Document):
    book = IntField(unique=True, required=True)
    book_word = StringField(max_length=25)
    title = StringField()
    cover_path = StringField()
    filename = StringField()
    html_path = StringField()
    filepath = StringField()
    text = StringField()
    meta = {"collection": "epubmetadata"}


class Metadata(me.Document):
    book = IntField()
    title = StringField()
    filename = StringField()
    filepath = StringField()
    html_path = StringField()
    text = StringField()
    meta = {"collection": "metadata"}


class Section(me.Document):
    section = IntField(min_value=1, max_value=17)
    title = StringField()
    book = IntField(min_value=1, max_value=10)
    chapters = ListField(IntField())
    start = IntField(min_value=1)
    end = IntField(max_value=3462)
    filename = StringField()
    mmd = StringField()
    mmd_path = StringField()
    md_path = StringField()
    md = StringField()
    html_path = StringField()
    html = StringField()
    section_files = ListField(StringField())

    def __int__(self):
        return self.section


class Titlepage(me.Document):
    book = IntField(Required=True, unique=True, Indexed=True)
    book_word = StringField(max_length=20)
    title = StringField(Required=True, max_length=500)
    text = StringField()
    filename = StringField()
    md_path = StringField()
    html_path = StringField()
    md = StringField()
    html = StringField()


def send_notification():
    load_dotenv("knock.env")
    apikey = os.environ.get("KNOCK_SECRET")
    client = Knock(api_key=apikey)
    client.notify(key="superforge", actor="maxludden", recipients=["user-2"], data={})


# > Backup
def backup_db(database: str) -> None:
    """
    Back up Database.

    Args:
        `collection` (str):
            The desired database to back up.
    """
    collections = [
        "Book",
        "ChapterNotFound",
        "Chapter",
        "chapter_gen",
        "Coverpage",
        "Defaultdoc",
        "EndOfBook",
        "EndOfBook",
        "Epubmeta",
        "Metadata",
        "Section",
        "Titlepage",
    ]

    dbs = ["SUPERGENE", "MAKE_SUPERGENE", "LOCALDB"]
    if database in dbs:
        sg(database)
        path = f"{BASE}/backup"
        log.debug(f"Backup Filepath: {path}")
        cd(path)

        result = mongodump("-d", "SUPERGENE", f'--archive="{path}/db.archive"')
        if result.exit_code == 0:
            now = datetime.isoformat(datetime.now())
            msg = f"Backed up {database} at {now}"
            log.debug(msg)
            finished(msg, filename="core.backupDB.py", title=f"{database} Archived")


backup_db("SUPERGENE")
