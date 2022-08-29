# superforge_poetry/variance.py

import re
from os import environ
from time import perf_counter
from alive_progress import alive_bar
from rich import print
from rich.columns import Columns
from rich.panel import Panel, ROUNDED
from rich.console import Group, Console
from rich.style import Style

from mongoengine import connect, Document
from mongoengine.fields import StringField, IntField, URLField


from log import log

console = Console()
# try:
#     from log import log, max_console
# except ModuleNotFoundError as ModNotFound:
#     from superforge_poetry.log import  log, max_console
# except ImportError as ImportError:
#     from superforge_poetry.log import  log, max_console


class Chapter(Document):
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


# > Connecting to the database
def sg(database: str = "LOCALDB"):
    """Custom mongoengine connection"""
    databases = ["SUPERGENE", "LOCALDB", "MAKE_SUPERGENE"]
    if database not in databases:
        raise ValueError(f"Database {database} not in {databases}")
    match database:
        case "SUPERGENE":
            URI = environ.get("SUPERGENE")
        case "LOCALDB":
            URI = environ.get("LOCALDB")
        case "MAKE_SUPERGENE":
            URI = environ.get("MAKE_SUPERGENE")
        case _:
            URI = environ.get("LOCALDB")
    try:
        connect("SUPERGENE", host=URI)
        log.debug(f"Connected to {database}")
    except ConnectionError as ce:
        log.error(f"Could not connect to {database}")
        raise ce


def find_variances():
    sg()
    t1 = perf_counter()
    chapters = []
    with alive_bar(3462, title="Finding Variance", dual_line=True) as bar:
        for doc in Chapter.objects():
            if doc.unparsed_text == doc.text:
                bar.text = f"Parsing chapter {doc.chapter}"
                bar()
                continue
            else:
                bar.text = f"Found variance in chapter {doc.chapter}."
                chapter_dict = {
                    "chapter": doc.chapter,
                    "section": doc.section,
                    "book": doc.book,
                }
                chapters.append(chapter_dict)
                bar()

    t2 = perf_counter()
    raw_duration = t2 - t1

    avg = raw_duration / 3460
    average = f"[green]{avg:.2f} seconds per chapter"

    if raw_duration > 60:
        duration_remainder = raw_duration % 60
        minutes = (raw_duration - duration_remainder) / 60
        duration = f"{minutes} minutes and {duration_remainder} seconds"
    else:
        duration = f"{raw_duration} seconds"

    green_style = Style(color="white", bgcolor="green", bold=True)
    elapsed_time = Panel(
        duration,
        box=ROUNDED,
        title="Elapsed Time",
        title_align="center",
        style=green_style,
    )

    blue_style = Style(color="white", bgcolor="blue", bold=True,)
    average_time = Panel(
        average,
        box=ROUNDED,
        title="Average Time",
        title_align="center",
        style=blue_style,
    )

    white_style = Style(color="black", bgcolor="white", bold=True,)
    variances = Panel(
        f"{len(chapters)}/3462",
        box=ROUNDED,
        title="Variances",
        title_align="center",
        style=white_style
    )

    stat_group = Group(elapsed_time, average_time)
    print(stat_group)
    print(variances)
    return chapters


def get_content(chapter_dict: dict[str]) -> str:
    """
    Generate a renderable string from the chapters.
    """
    title = f'[b][blue]Chapter {chapter_dict["chapter"]}'
    subtitle = f'[white]Section {chapter_dict["section"]}'
    content = f'[white]Book {chapter_dict["book"]}'
    return f"{title}\n{subtitle}\n{content}"


chapters = find_variances()
user_renderables = [Panel(get_content(chapter), expand=True) for chapter in chapters]
console.print(Columns(user_renderables))

if __name__ == "__main__":
    find_variances()
