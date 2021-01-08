# -*- coding: utf-8 -*-
# Module: default
# Author: solbero
# Created on: 13.12.2020
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

# Imports
from typing import Set, Callable, Union

import routing
import xbmcgui
import xbmcplugin

from . import lutris

# Aliases
Array = lutris.Array

# Globals
plugin = routing.Plugin()
game_list = lutris.check_cache('games', lutris.get_games)


@plugin.route('/')
def index():
    """Creates a main menu for the add-on"""
    xbmcplugin.addDirectoryItem(plugin.handle,
                                plugin.url_for(all),
                                xbmcgui.ListItem("All"),
                                True)
    # Check if the key 'platform' is in the GameArray. Do not display
    # this menu item if it is missing.
    if 'platform' not in game_list:
        xbmcplugin.addDirectoryItem(plugin.handle,
                                    plugin.url_for(platforms),
                                    xbmcgui.ListItem("Platforms"),
                                    True)

    # Check if the key 'runner' is in the GameArray. Do not display
    # this menu item if it is missing.
    if 'runner' not in game_list:
        xbmcplugin.addDirectoryItem(plugin.handle,
                                    plugin.url_for(runners),
                                    xbmcgui.ListItem("Runners"),
                                    True)

    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/all')
def all():
    """Creates game list items in Kodi for the 'All' folder."""
    directory_items = create_directory_items(game_list)

    xbmcplugin.addDirectoryItems(plugin.handle, directory_items)
    xbmcplugin.addSortMethod(plugin.handle,
                             xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/platforms')
def platforms():
    """Creates platform folders in Kodi based on platforms in the
    game array.

    """
    platform_directories = extract_unique_values(game_list, 'platform')
    directories = create_directories(platform_directories, platform)

    xbmcplugin.addDirectoryItems(plugin.handle, directories)
    xbmcplugin.addSortMethod(plugin.handle,
                             xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/platforms/<platform>')
def platform(platform: str):
    """Creates game list items in Kodi for a specific platform folder.

    Args:
        platform (str): Platform folder to populate.

    """
    games_platform: Array = extract_dicts_with_value(game_list, 'platform',
                                                     platform)
    directory_items = create_directory_items(games_platform)

    xbmcplugin.addDirectoryItems(plugin.handle, directory_items)
    xbmcplugin.addSortMethod(plugin.handle,
                             xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/runners')
def runners():
    """Creates runner folders in Kodi based on runners in the game array."""
    runners = extract_unique_values(game_list, 'runner')
    directories = create_directories(runners, runner)

    xbmcplugin.addDirectoryItems(plugin.handle, directories)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/runners/<runner>')
def runner(runner):
    """Creates game list items in Kodi for a specific platform folder.

    Args:
        platform (str): Platform folder to populate.

    """
    games_runner: Array = extract_dicts_with_value(game_list, 'runner', runner)

    directory_items = create_directory_items(games_runner)
    xbmcplugin.addDirectoryItems(plugin.handle, directory_items)
    xbmcplugin.addSortMethod(plugin.handle,
                             xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/run/<id_>')
def run(id_: str):
    """Runs a game list item.

    Args:
        id_ (str): Lutris numerical id.

    """
    lutris.run(id_)


@plugin.route('/lutris')
def lutris_():
    """Opens Lutris"""
    lutris.run()


@plugin.route('/update')
def update():
    """Rebuilds the plugin games cache."""
    lutris.rebuild_cache('games', lutris.get_games)


def create_directory_items(array: Array):
    """Creates a list of ListItems.

    Args:
        array (Array): List of dicts to create ListItems from.

    Returns:
        [type]: list of ListItem

    """
    xbmcplugin.setContent(plugin.handle, 'games')

    directory_items = []
    for dict_ in array:
        title = str(dict_['name'])
        slug = str(dict_['slug'])
        runner = str(dict_['runner'])
        platform = str(dict_['platform'])

        item = xbmcgui.ListItem(title, offscreen=True)
        item.setProperty('IsPlayable', 'true')
        item.setInfo('game', {'title': title,
                              'platform': platform,
                              'gameclient': runner})

        arts_dictionary = lutris.create_arts_dictionary(slug)
        item.setArt(arts_dictionary)

        id_ = dict_['id']
        url = plugin.url_for(run, id_)

        directory_items.append((url, item, False))

    return directory_items


def create_directories(labels: set, func: Callable):
    """Create a list of folder ListItems from a set of unique labels.

    Args:
        labels (set): Set of unique labels
        func (Callable): Fuction to pass to 'plugin.route'.

    Returns:
        [type]: List of ListItems.

    """
    xbmcplugin.setContent(plugin.handle, 'files')

    directories = []
    for label in labels:
        item = xbmcgui.ListItem(label.capitalize())
        item.setProperty('IsPlayable', 'false')

        url = plugin.url_for(func, label)
        directories.append((url, item, True))

    return directories


def extract_unique_values(array: Array, key: str) -> Set[Union[str, int]]:
    """Returns all unique labels from a list of dicts which matches a
    key.

    Args:
        array (Array): List of dicts to search.
        key (str): Key to find in dict.

    Returns:
        Set[Union[str, int]]: Set containing all unique values.
    """
    labels = {dict_[key] for dict_ in array}

    return labels


def extract_dicts_with_value(array: Array, key: str,
                             val: str) -> Array:
    """Returns all dictionaries from a list of dicts which matches a
    key-value pair.

    Args:
        array (Array): List of dicts to search.
        key (str): Key to find in dict.
        val (str): Value the key must equal in dictionary.

    Returns:
        Array: An array only containing dicts where 'key' matches 'value'.
    """
    extracted_dicts = [dict_ for dict_ in array if dict_[key] == val]

    return extracted_dicts


def main():
    plugin.run()
