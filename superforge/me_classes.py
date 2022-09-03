# superforge/me_classes.py

"""
This module is a collection of classes for the SuperForge project.
"""
from pathlib import Path
from typing import List, Optional, Union

from mongoengine import Document
from mongoengine.fields import (
    BooleanField,
    DateTimeField,
    IntField,
    ListField,
    StringField,
    URLField,
    UUIDField,
)

# custom exceptions


class MMDConversionException(Exception):
    pass


class ChapterNotFound(ValueError):
    pass


class InvalidPartException(Exception):
    pass


class MMDConversionError(Exception):
    pass


class SectionNotFound(ValueError):
    pass


class TitlepageNotFound(ValueError):
    pass


# > MongoEngine Models/Classes
class Book(Document):
    """This class contains the book metadata."""

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
    filepath = StringField()
    filepath = StringField()


class Chapter(Document):
    """This class contains the chapter content and metadata."""

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


class chapter_gen:
    """
    Generator to generate chapter numbers for SuperGene.

    Usage:
        chapters = chapter_gen()
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

    def __len__(self):
        return self.end - self.start + 1


class Coverpage(Document):
    book = IntField()
    filename = StringField()
    filepath = StringField()
    html_path = StringField()
    html = StringField()
    meta = {"collection": "coverpage"}


class Defaultdoc(Document):
    """This class stores documents used to generate the default file for each book."""

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


class EndOfBook(Document):
    """This class store the data to generate the End of Book files for each book."""

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


class Epubmeta(Document):
    """This class stores the epub metadata for each book."""

    book = IntField(unique=True, required=True)
    book_word = StringField(max_length=25)
    title = StringField()
    cover_path = StringField()
    filename = StringField()
    html_path = StringField()
    filepath = StringField()
    text = StringField()
    meta = {"collection": "epubmetadata"}


class Metadata(Document):
    """This class stores the metadata for each book."""

    book = IntField()
    title = StringField()
    filename = StringField()
    filepath = StringField()
    html_path = StringField()
    text = StringField()
    meta = {"collection": "metadata"}


class Section(Document):
    """This class stores the section content and metadata."""

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


class Titlepage(Document):
    """This class stores the titlepage content and metadata."""

    book = IntField(Required=True, unique=True, Indexed=True)
    book_word = StringField(max_length=20)
    title = StringField(Required=True, max_length=500)
    text = StringField()
    filename = StringField()
    md_path = StringField()
    html_path = StringField()
    md = StringField()
    html = StringField()
