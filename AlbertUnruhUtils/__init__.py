__author__ = "AlbertUnruh"
__url__ = "https://github.com/AlbertUnruh/AlbertUnruhUtils.py"
__license__ = "MIT"
__copyright__ = f"(c) {__author__}"
__version__ = "2021.11.13.000"  # pattern: 'YYYY.MM.DD.{increment:3}'
__description__ = "A collection of utils written in Python."

from . import config
from . import ratelimit

from .config import *
from .ratelimit import *
