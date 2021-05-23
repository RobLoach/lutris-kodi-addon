# -*- coding: utf-8 -*-
# Module: default
# Author: solbero
# Created on: 13.12.2020
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

# Imports
import errno
import json
import os
import shlex
import shutil
import subprocess
from typing import Dict, List, Union

import xbmcaddon

import lib.util as util

# Globals
_addon = xbmcaddon.Addon()


def _get_path() -> list:
    """Finds the path to the Lutris executable.

    Returns a custom path to the executable if it is defined in the
    add-on settings, otherwise locates the path automatically using
    'shutil.which()'.

    Raises:
        FileNotFoundError: If unable to find executable.

    Returns:
        path (list): Path to executable.

    """
    enable_custom_path = _addon.getSettingBool('enable_custom_path')

    if enable_custom_path:
        result = _addon.getSettingString('custom_path')
        _, tail = os.path.split(result)
        if tail != 'lutris':
            raise ValueError(f"Executable 'lutris' not in custom path '{result}'")
    else:
        result = shutil.which('lutris')
        if result is None:
            raise FileNotFoundError(errno.ENOENT,
                                    os.strerror(errno.ENOENT),
                                    'lutris')

    util.log(f"Executable path is: {result}")

    path = shlex.split(str(result))

    return path


@util.use_cache
def get_games() -> List[Dict[str, Union[str, int]]]:
    """Gets a list of dicts of installed games from Lutris.

    Note:
        List of dicts returned by the function looks as follows:
        [
        {
            "id": 74,
            "slug": "a-story-about-my-uncle",
            "name": "A Story About My Uncle",
            "runner": "steam",
            "platform": "Linux",
            "directory": ""
        },
        {
            ...
        }
        ]

    Returns:
        games (List[Dict[str, Union[str, int]]]): List of installed games.
    """
    path = _get_path()
    flags = ['--list-games', '--installed', '--json']
    command = path + flags

    raw = subprocess.check_output(command)
    parsed = json.loads(raw)

    util.log(f"JSON output is: {parsed}")

    return parsed


@util.on_playback
def run(args: Dict[str, List[str]]):
    """Runs a game using Lutris.

    Note:
        Lutris is opened if passed dict is does not contain key 'id' or 'slug'.

    Args
        args (dict): Key 'id' or 'slug' as pair of {key: value}.

    """
    path = _get_path()

    if 'id' in args:
        flag = [f"lutris:rungameid/{args['id'][0]}"]
        command = path + flag
    elif 'slug' in args:
        flag = [f"lutris:rungame/{args['slug'][0]}"]
        command = path + flag
    else:
        command = path

    util.log(f"Run command is: {' '.join(command)}")

    subprocess.run(command, check=True)


def get_art(slug: str) -> Dict[str, str]:
    """Creates a dict of available art for a game.

    Args:
        slug (str): Lutris game slug

    Returns:
        art (Dict[str, str]): Pairs of {key: path}.
    """
    art_paths = _get_art_paths(slug)

    art = {}
    for key, value in art_paths.items():
        if os.path.exists(value['path']):
            art[key] = value['path']
        else:
            if 'fallback' in value:
                art[key] = value['fallback']
            else:
                util.log(f"Unable to find '{key}' art for '{slug}'.")

    return art


def _get_art_paths(slug: str) -> Dict[str, Dict[str, str]]:
    """Gets paths to game art for a game.

    Args:
        slug (str): Lutris game slug

    Returns:
        art_paths (Dict[str, [Dict[str, str]]]): Pairs of {key: path}.
    """
    home = os.path.expanduser('~/')
    icons = os.path.join(home + '.local', 'share', 'icons',
                         'hicolor', '128x128', 'apps')
    lutris = os.path.join(home + '.local', 'share', 'lutris')

    icon_path = os.path.join(icons, f"lutris_{slug}.png")
    banner_path = os.path.join(lutris, 'banners', f"{slug}.jpg")
    cover_path = os.path.join(lutris, 'covers', f"{slug}.jpg")

    prefer_covers = _addon.getSettingBool('prefer_covers')

    art_paths = {}
    if prefer_covers:
        art_paths['icon'] = {'path': cover_path, 'fallback': icon_path}
        art_paths['thumb'] = {'path': cover_path, 'fallback': icon_path}
    else:
        art_paths['icon'] = {'path': icon_path}
        art_paths['thumb'] = {'path': icon_path}

    art_paths['banner'] = {'path': banner_path}
    art_paths['poster'] = {'path': cover_path, 'fallback': icon_path}

    return art_paths
