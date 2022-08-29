# superforge_poetry/

import re
from os import environ
from time import perf_counter
from tkinter import N
from typing import TYPE_CHECKING, Optional, Union
from json import dump, load

from alive_progress import alive_bar
from mongoengine import Document, connect
from mongoengine.fields import IntField, StringField, URLField
from rich import inspect, print
from rich.align import AlignMethod
from rich.box import ROUNDED, Box
from rich.columns import Columns
from rich.console import Console, Group, RenderableType
from rich.jupyter import JupyterMixin
from rich.markdown import Markdown
from rich.measure import Measurement, measure_renderables
from rich.padding import Padding, PaddingDimensions
from rich.panel import Panel
from rich.pretty import pprint
from rich.segment import Segment
from rich.style import Style, StyleType
from rich.terminal_theme import MONOKAI
from rich.text import Text, TextType
from rich.theme import Theme
from rich.layout import Layout
from tqdm.auto import tqdm

from log import log


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


# >┌──────────────────────────────────────────────────────┐< #
# >│                    Voice of God                      │< #
# >└──────────────────────────────────────────────────────┘< #
def find(pattern: str):
    with open("json/matches.json", "r") as infile:
        matches_dict = dict(load(infile))
    sg()
    beast_soul_chapters = {}
    # regex = r"^(.*?beast soul.*?:.*)$"
    # regex = r"^(.*?beast soul.*?;.*)$"
    # regex = r"^(.*?beast soul.*?hunted.*)$"
    # regex = r"^(.*?hunted.*?beast soul.*)$"
    regex = r"{pattern}".format(pattern=pattern)
    matches_dict[regex] = {}

    for doc in tqdm(Chapter.objects(), unit="ch", desc="Beast Soul"):
        unparsed_text = doc.unparsed_text
        matches = re.findall(regex, unparsed_text, re.MULTILINE)

        if matches:
            if len(matches) > 1:
                current_matches = []
                for match in matches:
                    sentances = len(match.split("."))
                    if sentances > 2:
                        current_matches.append(match)
            else:
                sentances = len(matches[0].split("."))
                if sentances > 2:
                    current_matches = matches
            if current_matches:
                matches_dict[regex][doc.chapter] = current_matches

    with open("json/matches.json", "w") as outfile:
        dump(matches_dict, outfile, indent=4)

    finished_panel = Panel(
        Text("Beast Soul Chapters", justify="center"),
        style=Style(color="green", bold=True),
        title="Finished",
    )
    print(finished_panel)


def table_beast():
    with open("json/matches.json", "r") as infile:
        matches_dict = dict(load(infile))

    sg()
    matches_dict["blockquote"] = {}
    for doc in tqdm(Chapter.objects(), unit="ch", desc='<table class="beast">'):
        md = doc.md
        matches = re.findall(r"^(>.*)$", md, re.I)
        if matches:
            matches_dict["blockquote"][doc.chapter] = matches

    with open("json/matches.json", "w") as outfile:
        dump(matches_dict, outfile, indent=4)

    finished_panel = Panel(
        Text("VoG", justify="center"),
        style=Style(color="green", bold=True),
        title="Finished",
    )
    print(finished_panel)


def blood_pulse():
    sg("SUPERGENE")
    panels = []
    for doc in tqdm(Chapter.objects(), unit="ch", desc="Blood Pulse"):
        text = doc.text
        edited = False
        if "Blood – Pulse" in text:
            text.replace("Blood – Pulse", "Blood-Pulse")
            edited = True
        if "Blood – pulse" in text:
            text.replace("Blood – pulse", "Blood-Pulse")
            edited = True
        if "blood pulse" in text:
            text.replace("blood pulse", "blood-pulse")
            edited = True
        if edited == True:
            print(
                Text(
                    f"{doc.chapter}",
                    justify="center",
                    style=Style(color="blue", bold=True),
                )
            )
            # panel=Panel(
            #     Text(
            #         f"{doc.chapter}",
            #         style=Style(
            #             color="#fdfdfd",
            #             bgcolor="#222222",
            #             justify="center"
            #             )
            #     ),
            #     title = Text(
            #         "Found In",
            #         justify="center",
            #         style=Style(
            #             color="white", bold=True
            #         )
            #     ),
            #     style=Style(
            #         color="blue", bgcolor="#222222"
            #     )
            # )
            panels.append(panel)
            doc.text = text
            doc.save()

    finished_panel = Panel(Columns(panels))
    print(finished_panel)

    def beast_div():
    table_chapters = [
        "3",
        "8",
        "10",
        "26",
        "53",
        "68",
        "82",
        "118",
        "120",
        "146",
        "161",
        "188",
        "246",
        "285",
        "305",
        "339",
        "369",
        "388",
        "443",
        "485",
        "487",
        "494",
        "508",
        "520",
        "545",
        "617",
        "701",
        "739",
        "783",
        "1044",
        "1073",
        "1074",
        "1133",
        "1223",
        "1224",
        "1228",
        "1241",
        "1245",
        "1246",
        "1275",
        "1449",
        "1454",
        "1492",
        "1521",
        "1606",
        "1616",
        "1729",
        "1750",
        "1859",
        "2008",
        "2138",
        "2158",
        "2214",
        "2222",
        "2316",
        "2355",
        "2361",
        "2396",
        "2450",
        "2494",
        "2521",
        "2579",
        "2809",
        "2893",
        "3060",
        "3067",
        "3085",
        "3087",
        "3118",
        "3166",
    ]

    for x, ch in enumerate(table_chapters):
        if x == 0:
            result = ch
        else:
            result += "\n" + ch
    with open("../json/table_chapters.txt", "w") as outfile:
        outfile.write(result