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
from typing import List, Union, Dict, Callable

import simplecache
import xbmcaddon

from . import util

# Aliases
Array = List[Dict[str, Union[str, int]]]

# Globals
addon_id = xbmcaddon.Addon()
addon_name = addon_id.getAddonInfo('name')
localized_string = addon_id.getLocalizedString

cache = simplecache.SimpleCache()
cache.enable_mem_cache = False


def get_path() -> list:
    """Finds the path to the Lutris executable.

    Returns a custom path to the executable if it is defined in the
    add-on settings, otherwise locates the path automatically using
    'distutil.spawn.find_executable()'.

    Raises:
        FileNotFoundError: If unable to find executable.

    Returns:
        list: Path to executable.

    """
    if addon_id.getSettingBool('enable_custom_path'):
        try:
            result = addon_id.getSettingString('path_to_executable')
            if not os.path.isfile(result):
                raise FileNotFoundError(errno.ENOENT,
                                        os.strerror(errno.ENOENT),
                                        result)
        except FileNotFoundError:
            util.show_error(localized_string(30201))
    else:
        try:
            result = find_executable('lutris')
            if result is None:
                raise FileNotFoundError(errno.ENOENT,
                                        os.strerror(errno.ENOENT),
                                        'lutris')
        except FileNotFoundError:
            util.show_error(localized_string(30201))

    util.log(f"Executable path is: {result}")
    path = shlex.split(str(result))

    return path


def get_games() -> Array:
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
    executable = get_path()
    flags = ['--list-games', '--installed', '--json']
    command = executable + flags

    try:
        result = subprocess.check_output(command)
    except subprocess.CalledProcessError:
        util.show_error(localized_string(20202))

    try:
        response = json.loads(result)
    except json.JSONDecodeError:
        util.show_error(localized_string(30203))

    util.log(f"JSON output is: {response}")

    return response


def run(id_: str = None):
    """Runs a game using Lutris.

    Note:
        Lutris is opened if 'id_' is not passed.

    Args:
        id_ (str, optional): Lutris numerical id. Defaults to None.

    """
    path = get_path()

    if id_:
        flag = [f"lutris:rungameid/{id_}"]
        command = path + flag
    else:
        command = path

    util.log(f"Launch command is: {' '.join(command)}")

    util.stop_playback()
    util.inhibit_idle_shutdown(True)

    try:
        subprocess.run(command, check=True)

    except subprocess.CalledProcessError:
        util.show_error(f"{localized_string(30203)}")

    util.inhibit_idle_shutdown(False)


def check_cache(endpoint: str, func: Callable, *args, **kwargs) -> Array:
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
    cache_ = cache.get(f"{addon_name}.{endpoint}")

    if cache_:
        array = cache_
    else:
        array = rebuild_cache(endpoint, func, *args, **kwargs)

    return array


def rebuild_cache(id_: str, func, *args, **kwargs) -> Array:
    """Gets an array object using the supplied function and caches it.

    Args:
        endpoint (str): Name of cache object.
        func (Callable): Function to call.
        *args: 'func' arguments.
        **kwargs: 'func' keyword arguments.

    Returns:
        array (Array): Array returned by 'func'.

    """
    array = func(*args, **kwargs)

    if addon_id.getSettingBool('enable_cache'):
        hours = float(addon_id.getSettingInt('cache_expire_hours'))
        days = float(addon_id.getSettingInt('cache_expire_days'))
        total = hours + (days * 24)
    else:
        total = float(0)

    expiration = datetime.timedelta(hours=total)

    util.notify_user(localized_string(30302))
    cache.set(f"{addon_name}.{id_}", array, expiration=expiration)

    return array


def create_arts_dictionary(slug: str) -> Dict[str, str]:
    """Creates a dict of available artwork.

    Args:
        slug (str): Lutris game slug

    Returns:
        Dict[str, str]: Pairs of {key: path}.
    """
    art_paths = get_art_paths(slug)

    arts_dictionary = {}
    for key, value in art_paths.items():
        if os.path.exists(value['path']):
            arts_dictionary[key] = value['path']
        else:
            if 'fallback' in value:
                arts_dictionary[key] = value['fallback']
            else:
                util.log(f"Unable to find {key} art for {slug}.")

    return arts_dictionary


def get_art_paths(slug: str):
    """Get paths to artwork.

    Args:
        slug (str): Lutris game slug

    Returns:
        dict: Pairs of {key: path}.
    """
    home = os.path.expanduser('~/')
    home_share_icons = os.path.join(home + '.local', 'share', 'icons',
                                    'hicolor', '128x128', 'apps')
    home_share_lutris = os.path.join(home + '.local', 'share', 'lutris')
    icon_path = os.path.join(home_share_icons, f"lutris_{slug}.png")
    banner_path = os.path.join(home_share_lutris, 'banners', f"{slug}.jpg")
    cover_path = os.path.join(home_share_lutris, 'covers', f"{slug}.jpg")

    art_paths = {}
    if addon_id.getSettingBool('prefer_covers'):
        art_paths['icon'] = {'path': cover_path, 'fallback': icon_path}
        art_paths['thumb'] = {'path': cover_path, 'fallback': icon_path}
    else:
        art_paths['icon'] = {'path': icon_path}
        art_paths['thumb'] = {'path': icon_path}
    art_paths['banner'] = {'path': banner_path}
    art_paths['poster'] = {'path': cover_path, 'fallback': icon_path}

    return art_paths
