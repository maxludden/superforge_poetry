# superforge_poetry/main.py

from ujson import load, dump
from os import environ
from pathlib import Path
import sh
from rich import *

from rich.traceback import install
from dotenv import load_dotenv, dotenv_values
from mongoengine import connect
from tqdm.auto import tqdm


from superforge.me_classes import chapter_gen, Chapter
from superforge_poetry.atlas import init

load_dotenv("env/.env")
URI = environ.get("LOCALDB")
connect("SUPERGENE", host=URI)

chapters = Chapter.objects().to_list()



# > Read toc files
toc1_path = Path("json/toc1.json")
with open (toc1_path, 'r') as infile:
    toc1 = dict(load(infile))

toc2_path = Path("json/toc2.json")
with open (toc2_path, 'r') as infile:
    toc2 = dict(load(infile))


#> Concatenate toc1 and toc2
URI = environ.get("LOCALDB")
connect("SUPERGENE", host=URI)

toc = {}
chapters = chapter_gen()
for x in tqdm(chapters, unit='ch', desc='Updating TOC'):
    doc = Chapter.objects(chapter=x).first()
    chapter_num = str(doc.chapter)
    title = toc1[chapter_num]["title"]
    if title != doc.title:
        doc.title = title
        doc.save()
    url = toc2[chapter_num]["url"]
    if url != doc.url:
        doc.url = url
        doc.save()
    toc[chapter_num] = {"title": title, "url": url}

#> Write toc to file
toc_path = Path("json/toc.json")
with open (toc_path, 'w') as outfile:
    dump(toc, outfile, indent=4)