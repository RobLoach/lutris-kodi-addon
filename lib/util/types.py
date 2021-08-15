# -*- coding: utf-8 -*-
# Module: default
# Author: solbero
# Created on: 15.08.2021
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

# Imports
from dataclasses import dataclass
from typing import List, Union


# Dataclasses
@dataclass
class LutrisGameInfo:
    id: str
    slug: str
    title: str
    platform: str
    runner: str


@dataclass
class TGDBGameInfo:
    platform: str
    genres: List[str]
    publishers: List[str]
    developers: List[str]
    overview: str
    release_year: Union[int, None]


@dataclass
class GameArtPaths:
    banner: str = ''
    boxart: str = ''
    clearlogo: str = ''
    fanart: str = ''
    screenshot: str = ''
