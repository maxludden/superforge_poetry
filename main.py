# superforge_poetry/main.py

from json import load
from os import environ
from pathlib import Path
import sh
from rich import *

from rich.traceback import install
from dotenv import load_dotenv, dotenv_values


load_dotenv()