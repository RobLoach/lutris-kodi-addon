# -*- coding: utf-8 -*-
# Module: default
# Author: solbero
# Created on: 13.12.2020
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

# Imports
from typing import Callable, Dict, List, Set, Union

import routing
import xbmcgui
import xbmcplugin

import lib.lutris as lutris

# Globals
_plugin = routing.Plugin()
_addon_handle = _plugin.handle


@_plugin.route('/')
def index():
    """Creates a main menu for the add-on"""
    games = lutris.get_cached_games()
    is_folder = True

    xbmcplugin.addDirectoryItem(_addon_handle,
                                _plugin.url_for(all),
                                xbmcgui.ListItem("All"),
                                is_folder)
    # Check if the key 'platform' is in the list of dicts. Do not display
    # this menu item if it is missing.
    if 'platform' in games[0]:
        xbmcplugin.addDirectoryItem(_addon_handle,
                                    _plugin.url_for(platforms),
                                    xbmcgui.ListItem("Platforms"),
                                    is_folder)

    # Check if the key 'runner' is in the list of dicts. Do not display
    # this menu item if it is missing.
    if 'runner' in games[0]:
        xbmcplugin.addDirectoryItem(_addon_handle,
                                    _plugin.url_for(runners),
                                    xbmcgui.ListItem("Runners"),
                                    is_folder)

    xbmcplugin.endOfDirectory(_addon_handle)


@_plugin.route('/all')
def all():
    """Creates game list items in Kodi for the 'All' folder."""
    games = lutris.get_cached_games()

    set_items_list(games)


@_plugin.route('/platforms')
def platforms():
    """Creates platform folders in Kodi based on platforms in the
    game array.

    """
    games = lutris.get_cached_games()
    platforms = {game['platform'] for game in games}

    set_directory_list(platforms, platform)


@_plugin.route('/platforms/<platform>')
def platform(platform: str):
    """Creates game list items in Kodi for a specific platform folder.

    Args:
        platform (str): Platform folder to populate.

    """
    games = lutris.get_cached_games()
    platform_games = [game for game in games if game['platform'] == platform]

    set_items_list(platform_games)


@_plugin.route('/runners')
def runners():
    """Creates runner folders in Kodi based on runners in the game array."""
    games = lutris.get_cached_games()
    runners = {game['runner'] for game in games}

    set_directory_list(runners, runner)


@_plugin.route('/runners/<runner>')
def runner(runner: str):
    """Creates game list items in Kodi for a specific platform folder.

    Args:
        platform (str): Platform folder to populate.

    """
    games = lutris.get_cached_games()
    runner_games = [game for game in games if game['runner'] == runner]

    set_items_list(runner_games)


@_plugin.route('/run')
def run():
    """Runs a game list item."""
    args = _plugin.args['args']
    print(args)
    lutris.run(args)


@_plugin.route('/update')
def update():
    """Updates the games cache."""
    lutris.update_cache()


def set_items_list(games: List[Dict[str, Union[str, int]]]):
    """Creates a list of ListItems.

    Args:
        array (Array): List of dicts to create ListItems from.
    """
    xbmcplugin.setContent(_addon_handle, 'games')
    xbmcplugin.addSortMethod(_addon_handle,
                             xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

    for game in games:
        title = str(game['name'])
        slug = str(game['slug'])
        runner = str(game['runner'])
        platform = str(game['platform'])
        id = str(game['id'])

        art = lutris.get_art(slug)
        url = _plugin.url_for(run, args=f"lutris:rungameid/{id}")
        is_folder = False

        item = xbmcgui.ListItem(title, offscreen=True)
        item.setProperty('IsPlayable', 'true')
        item.setInfo('game', {'title': title,
                              'platform': platform,
                              'gameclient': runner})
        item.setArt(art)

        xbmcplugin.addDirectoryItem(_addon_handle, url, item, is_folder)

    xbmcplugin.endOfDirectory(_addon_handle)


def set_directory_list(entries: Set[str], func: Callable):
    """Create a list of folder ListItems from a set of unique labels.

    Args:
        labels (set): Set of unique labels
        func (Callable): Fuction to pass to 'plugin.route'.
    """
    xbmcplugin.setContent(_addon_handle, 'files')
    xbmcplugin.addSortMethod(_addon_handle,
                             xbmcplugin.SORT_METHOD_LABEL)

    for entry in entries:
        url = _plugin.url_for(func, entry)
        is_folder = True

        item = xbmcgui.ListItem(entry.capitalize())
        item.setProperty('IsPlayable', 'false')

        xbmcplugin.addDirectoryItem(_addon_handle, url, item, is_folder)

    xbmcplugin.endOfDirectory(_addon_handle)


def main():
    _plugin.run()
