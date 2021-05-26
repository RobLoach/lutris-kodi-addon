# -*- coding: utf-8 -*-
# Module: default
# Author: solbero
# Created on: 13.12.2020
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

# Imports
from typing import Callable, Dict, List, Set, Union

import routing
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib import lutris
from resources.lib import util

# Globals
_plugin = routing.Plugin()
_addon = xbmcaddon.Addon()
_addon_handle = _plugin.handle
_localized = _addon.getLocalizedString


@_plugin.route('/')
def index():
    """Creates an index menu for the add-on"""
    games = lutris.get_games()

    xbmcplugin.addDirectoryItem(_addon_handle,
                                _plugin.url_for(all),
                                xbmcgui.ListItem("All"),
                                isFolder=True)

    if check_key('runner', games):
        xbmcplugin.addDirectoryItem(_addon_handle,
                                    _plugin.url_for(runners),
                                    xbmcgui.ListItem("Runners"),
                                    isFolder=True)

    if check_key('platform', games):
        xbmcplugin.addDirectoryItem(_addon_handle,
                                    _plugin.url_for(platforms),
                                    xbmcgui.ListItem("Platforms"),
                                    isFolder=True)

    xbmcplugin.endOfDirectory(_addon_handle)


@_plugin.route('/all')
def all():
    """Creates a folder that list all managed games"""
    games = lutris.get_games()

    set_items_list(games)


@_plugin.route('/platforms')
def platforms():
    """Creates platform folders based on the platforms of managed games."""
    games = lutris.get_games()
    platforms = {str(game['platform']) for game in games}

    set_directory_list(platforms, platform)


@_plugin.route('/platforms/<platform>')
def platform(platform: str):
    """Lists games in a specific platform folder.

    Args:
        platform (str): Platform folder to populate.
    """
    games = lutris.get_games()
    platform_games = [game for game in games if game['platform'] == platform]

    set_items_list(platform_games)


@_plugin.route('/runners')
def runners():
    """Creates runner folders based on the runners of managed games."""
    games = lutris.get_games()
    runners = {str(game['runner']) for game in games}

    set_directory_list(runners, runner)


@_plugin.route('/runners/<runner>')
def runner(runner: str):
    """List games in a specific runner folder.

    Args:
        runner (str): Runner folder to populate.
    """
    games = lutris.get_games()
    runner_games = [game for game in games if game['runner'] == runner]

    set_items_list(runner_games)


@_plugin.route('/run')
def run():
    """Runs a game

    Note:
        Passes the 'kwargs' of 'plugin.url_for()' as a dict to 'lutris.run'.
        If dict is empty Lutris is opened.
    """
    args = _plugin.args

    lutris.run(args)


@_plugin.route('/delete')
def delete():
    """Deletes the add-on cache."""
    util.notify_user(_localized(30302))
    util.delete_cache()


def set_items_list(games: List[Dict[str, Union[str, int]]]):
    """Creates list items from the supplied games list.

    Args:
        games (List[Dict[str, Union[str, int]]]): Games list to create list
            items from.
    """
    xbmcplugin.setContent(_addon_handle, 'games')
    xbmcplugin.addSortMethod(_addon_handle,
                             xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

    for game in games:
        id = str(game['id'])
        slug = str(game['slug'])
        title = str(game['name'])
        runner = str(game.get('runner', _localized(30207)))
        platform = str(game.get('platform', _localized(30207)))

        art = lutris.get_art(slug)
        url = _plugin.url_for(run, id=id, slug=slug, title=title, runner=runner, platform=platform)

        item = xbmcgui.ListItem(title, offscreen=True)
        item.setProperty('IsPlayable', 'true')
        item.setInfo('game', {'title': title,
                              'platform': platform,
                              'gameclient': runner})
        item.setArt(art)

        xbmcplugin.addDirectoryItem(_addon_handle, url, item,
                                    isFolder=False, totalItems=len(games))

    xbmcplugin.endOfDirectory(_addon_handle)


def set_directory_list(labels: Set[str], func: Callable):
    """Creates folder items from a set of labels.

    Args:
        labels (set): Set of unique labels
        func (Callable): Function to pass to 'plugin.route'.
    """
    xbmcplugin.setContent(_addon_handle, 'files')
    xbmcplugin.addSortMethod(_addon_handle,
                             xbmcplugin.SORT_METHOD_LABEL)

    for label in labels:
        url = _plugin.url_for(func, label)

        item = xbmcgui.ListItem(label.capitalize())
        item.setProperty('IsPlayable', 'false')

        xbmcplugin.addDirectoryItem(_addon_handle, url, item, isFolder=True)

    xbmcplugin.endOfDirectory(_addon_handle)


def check_key(key: str, games: List[Dict[str, Union[str, int]]]) -> bool:
    """Searches for value in games list.

    Args:
        games (List[Dict[str, Union[str, int]]])): Games list to search.

    Returns:
        bool (bool): True if value is found, else False.
    """
    for game in games:
        if game.get(key):
            return True

    return False


def main():
    _plugin.run()
