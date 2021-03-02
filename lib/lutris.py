# -*- coding: utf-8 -*-
# Module: default
# Author: solbero
# Created on: 13.12.2020
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

# Imports
import datetime
import errno
import json
import os
import shlex
import subprocess
from distutils.spawn import find_executable
from typing import Dict, List, Union

import simplecache
import xbmcaddon

import lib.util as util

# Globals
_addon_id = xbmcaddon.Addon()
_addon_name = _addon_id.getAddonInfo('name')
_localized = _addon_id.getLocalizedString

_cache = simplecache.SimpleCache()


def _get_path() -> list:
    """Finds the path to the Lutris executable.

    Returns a custom path to the executable if it is defined in the
    add-on settings, otherwise locates the path automatically using
    'distutil.spawn.find_executable()'.

    Raises:
        FileNotFoundError: If unable to find executable.

    Returns:
        list: Path to executable.

    """
    enable_custom_path = _addon_id.getSettingBool('enable_custom_path')

    if enable_custom_path:
        result = _addon_id.getSettingString('custom_path')
        if not os.path.isfile(result):
            util.show_error(_localized(30201))
            raise FileNotFoundError(errno.ENOENT,
                                    os.strerror(errno.ENOENT),
                                    result)
    else:
        result = find_executable('lutris')
        if result is None:
            util.show_error(_localized(30201))
            raise FileNotFoundError(errno.ENOENT,
                                    os.strerror(errno.ENOENT),
                                    'lutris')

    util.log(f"Executable path is: {result}")

    path = shlex.split(str(result))

    return path


def _get_games() -> List[Dict[str, Union[str, int]]]:
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
        array: List of dictionaries of installed games.

    """
    command = _get_path()
    flags = ['--list-games', '--installed', '--json']
    command.extend(flags)

    try:
        result = subprocess.check_output(command)
    except subprocess.CalledProcessError:
        util.show_error(_localized(20202))
        raise

    try:
        response = json.loads(result)
    except json.JSONDecodeError:
        util.show_error(_localized(30203))
        raise

    util.log(f"JSON output is: {response}")

    return response


def get_cached_games() -> List[Dict[str, Union[str, int]]]:
    """Checks if a cached array object exists, if not it gets
    the array object using the supplied function and caches it.

    Args:
        endpoint (str): Name of the cache object.
        func (Callable): Function to call.
        *args: 'func' arguments.
        **kwargs: 'func' keyword arguments.

    Returns:
        array (Array): Array returned by 'func'.

    """
    cached_games = _cache.get(f"{_addon_name}.{'games'}")

    if cached_games:
        games = cached_games
    else:
        games = update_cache()

    return games


def update_cache() -> List[Dict[str, Union[str, int]]]:
    """Gets an array object using the supplied function and caches it.

    Args:
        endpoint (str): Name of cache object.
        func (Callable): Function to call.
        *args: 'func' arguments.
        **kwargs: 'func' keyword arguments.

    Returns:
        array (Array): Array returned by 'func'.

    """
    games = _get_games()

    if _addon_id.getSettingBool('enable_cache'):
        hours = float(_addon_id.getSettingInt('cache_expire_hours'))
        days = float(_addon_id.getSettingInt('cache_expire_days'))
        total = hours + (days * 24)
    else:
        total = float(0)

    expiration = datetime.timedelta(hours=total)

    util.notify_user(_localized(30302))

    _cache.set(f"{_addon_name}.{'games'}", games, expiration=expiration)

    return games


def run(*args: List[str]):
    """Runs a game using Lutris.

    Note:
        Lutris is opened if 'id_' is not passed.

    Args:
        id_ (str, optional): Lutris numerical id. Defaults to None.

    """
    command = _get_path()

    if args:
        for arg in args:
            command.extend(arg)

    util.log(f"Launch command is: {' '.join(command)}")

    util.stop_playback()
    util.inhibit_idle_shutdown(True)

    try:
        subprocess.run(command, check=True)

    except subprocess.CalledProcessError:
        util.show_error(f"{_localized(30203)}")
        raise

    util.inhibit_idle_shutdown(False)


def get_art(slug: str) -> Dict[str, str]:
    """Creates a dict of available artwork.

    Args:
        slug (str): Lutris game slug

    Returns:
        Dict[str, str]: Pairs of {key: path}.
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
                util.log(f"Unable to find {key} art for {slug}.")

    return art


def _get_art_paths(slug: str):
    """Get paths to artwork.

    Args:
        slug (str): Lutris game slug

    Returns:
        dict: Pairs of {key: path}.
    """
    home = os.path.expanduser('~/')
    icons = os.path.join(home + '.local', 'share', 'icons',
                                    'hicolor', '128x128', 'apps')
    lutris = os.path.join(home + '.local', 'share', 'lutris')

    icon_path = os.path.join(icons, f"lutris_{slug}.png")
    banner_path = os.path.join(lutris, 'banners', f"{slug}.jpg")
    cover_path = os.path.join(lutris, 'covers', f"{slug}.jpg")

    prefer_covers = _addon_id.getSettingBool('prefer_covers')

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
