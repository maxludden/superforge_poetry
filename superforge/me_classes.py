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

from superforge_poetry.log import log

# custom exceptions


class MMDConversionException(Exception):
    pass


class ChapterNotFound(ValueError):
    pass


class InvalidChapter(ValueError):
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
    meta = {
        "indexes": ["book", "section", "chapter"],
        "ordering": ["book", "section", "chapter"],
        "abstract": True,
    }

    def generate_section(self):
        """
        Generate the section number for the given chapter.

        Raises:
            `InvalidChapter`
                ValueError: Invalid chapter number.


        Returns:
            `section` (int):
                The section for the given chapter.
        """
        if self.section:
            return self.section
        else:
            chapter = self.chapter
            if chapter in range(1, 3463):
                if chapter <= 424:
                    self.section = 1
                    self.save()
                    return 1
                elif chapter <= 882:
                    self.section = 2
                    self.save()
                    return 2
                elif chapter <= 1338:
                    self.section = 3
                    self.save()
                    return 3
                elif chapter <= 1679:
                    self.section = 4
                    self.save()
                    return 4
                elif chapter <= 1711:
                    self.section = 5
                    self.save()
                    return 5
                elif chapter <= 1821:
                    self.section = 6
                    self.save()
                    return 6
                elif chapter <= 1960:
                    self.section = 7
                    self.save()
                    return 7
                elif chapter <= 2165:
                    self.section = 8
                    self.save()
                    return 8
                elif chapter <= 2204:
                    self.section = 9
                    self.save()
                    return 9
                elif chapter <= 2299:
                    self.section = 10
                    self.save()
                    return 10
                elif chapter <= 2443:
                    self.section = 11
                    self.save()
                    return 11
                elif chapter <= 2639:
                    self.section = 12
                    self.save()
                    return 12
                elif chapter <= 2765:
                    self.section = 13
                    self.save()
                    return 13
                elif chapter <= 2891:
                    self.section = 14
                    self.save()
                    return 14
                elif chapter <= 3033:
                    if chapter == 3095:
                        log.warning(
                            f"Chapter {chapter} was inputted to generate_section().\nChapter {chapter} does not exist."
                        )
                    elif chapter == 3117:
                        log.warning(
                            f"Chapter {chapter} was inputted to generate_section(). \nChapter {chapter} does not exist."
                        )
                        pass
                    else:
                        self.section = 15
                        self.save()
                        return 15
                elif chapter <= 3303:
                    self.section = 16
                    self.save()
                    return 16
                elif chapter <= 3462:
                    self.section = 17
                    self.save()
                    return 17
                else:
                    raise InvalidChapter("Invalid Chapter", f"\nChapter: {chapter}")
            else:
                raise InvalidChapter("Invalid Chapter", f"\nChapter: {chapter}")

    def generate_book(self):
        """
        Generate the book number for the given chapter.

        Raises:
            `InvalidChapter`
                ValueError: Invalid chapter number.


        Returns:
            `book` (int):
                The book for the given chapter.
        """
        if self.book:
            return self.book
        else:
            if self.section:
                section = self.section
            else:
                section = self.generate_section()
            match section:
                case 1:
                    self.book = 1
                    self.save()
                    return 1
                case 2:
                    self.book = 2
                    self.save()
                    return 2
                case 3:
                    self.book = 3
                    self.save()
                    return 3
                case 4 | 5:
                    self.book = 4
                    self.save()
                    return 4
                case 6 | 7:
                    self.book = 5
                    self.save()
                    return 5
                case 8 | 9:
                    self.book = 6
                    self.save()
                    return 6
                case 10 | 11:
                    self.book = 7
                    self.save()
                    return 7
                case 12 | 13:
                    self.book = 8
                    self.save()
                    return 8
                case 14 | 15:
                    self.book = 9
                    self.save()
                    return 9
                case 16 | 17:
                    self.book = 10
                    self.save()
                    return 10
                case _:
                    raise InvalidChapter(
                        "Invalid Chapter", f"\nChapter: {self.chapter}"
                    )

    def generate_filename(self):
        """Generate the filename for the given chapter."""
        if self.filename:
            return self.filename
        else:
            chapter_str = str(self.chapter).zfill(4)
            filename = f"chapter_{chapter_str}"
            self.filename = filename
            self.save()
            return filename

    def generate_md_path(self, force: bool = False):
        """
        Generate the path for the given chapters markdown file.

        Raises:
            `InvalidChapter`
                ValueError: Invalid chapter number.

        Args:
                `force` (bool):
                    Force the generation of the path.

        Returns:
            `md_path` (str):
                The path for the given chapters markdown file.
        """
        # book
        if self.book:
            book = self.book
        else:
            book = self.generate_book()

        # filename
        if self.filename:
            filename = self.filename
        else:
            filename = self.generate_filename()

        # determine the book directory
        book_zfill = str(book).zfill(2)

        # generate the md_path
        md_path = f"books/book{book_zfill}/md/{filename}.md"
        self.md_path = md_path
        self.save()
        return md_path

    def generate_html_path(self, force: bool = False):
        """
        Generate the path for the given chapters html file.

        Raises:
        `InvalidChapter`
            ValueError: Invalid chapter number.

        Args:
            `force` (bool):
                Force the generation of the path.

        Returns:
            `html_path` (str):
                The path for the given chapters html file.
        """
        # book
        if self.book:
            book = self.book
        else:
            book = self.generate_book()

        # filename
        if self.filename:
            filename = self.filename
        else:
            filename = self.generate_filename()

        # determine the book directory
        book_zfill = str(book).zfill(2)

        # generate the html_path
        html_path = f"books/book{book_zfill}/html/{filename}.html"
        self.html_path = html_path
        self.save()
        return html_path

    # def


class chapter_gen:
    """
    Generator to generate chapter numbers for SuperGene.

    Usage:
        chapters = chapter_gen()
    """


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

    def __len__(self):
        return self.end - self.start + 1

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
