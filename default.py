# -*- coding: utf-8 -*-
# Module: default
# Author: ???
# Created on: ???
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

import os
import sys
import urllib

import simplejson as json
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib.helpers import *
from resources.lib.lutrisapi import LutrisAPI
from resources.lib.lutriscmd import LutrisCMD

# Get the plugin url in plugin:// notation.
base_url = sys.argv[0]
# Get the plugin handle as an integer number.
addon_handle = int(sys.argv[1])
# Get the addon settings
addon_settings = xbmcaddon.Addon(id='script.lutris')
# Get the addon name from addon settings
addon_name = addon_settings.getAddonInfo('name')
# Plugin User Data Folder
userdata = addon_settings.getAddonInfo('path')
# Lutris User Data Folder
lutris_data = os.path.join(os.path.expanduser('~'), '.local', 'share', 'lutris')
# Get the localized string from addon settings
localized_string = addon_settings.getLocalizedString
# Create a Lutris API Client
LutrisClient = LutrisAPI()
# Create a Lutris CMD Client

executable = None
# Check if the user has specified a custom path to the lutris executable
if addon_settings.getSetting('use_custom_path') == 'true':
    # Get the path from addon settings
    executable = addon_settings.getSetting('lutris_executable')
Lutris = LutrisCMD(executable)


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument: value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: string
    """
    return '{0}?{1}'.format(base_url, urllib.urlencode(kwargs))


def list_games():
    """Create the list of games in the Kodi interface."""
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(addon_handle, 'My Lutris Collection')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(addon_handle, 'games')
    # Create a list to hold the games
    list_items = []
    # Add the Launch Lutris item
    li = xbmcgui.ListItem(label=addon_name)
    # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
    li.setArt({'fanart': addon_settings.getAddonInfo('fanart'), 'thumb': addon_settings.getAddonInfo('icon')})
    url = get_url(action='play', id='-', name=addon_name)
    # is_folder = False means that this item won't open any sub-list.
    is_folder = False
    # Add the item to item list
    list_items.append((url, li, is_folder))
    # Get list of games and convert to UTF8
    games = convert_to_utf8(Lutris.listGames(installed=True, json=False))
    # Iterate through the games
    for game in games:
        # Create a list item with a text label and a thumbnail image.
        li = xbmcgui.ListItem(label=game['name'])
        # Get game information and artwork from Lutris.net if possible and save to local userdata folder
        icon_path = os.path.join(lutris_data, 'icons', gamedata['slug'] + '.png')
        banner_path = os.path.join(lutris_data, 'banners', gamedata['slug'] + '.jpg')
        info_path = os.path.join(userdata, gamedata['slug'] + '.json')
        try:
            gamedata = LutrisClient.getGameBySlug(game['slug'])
            if not os.path.exists(icon_path) and gamedata['icon_url'] is not None:
                icon = LutrisClient.getIcon(gamedata['icon_url'])
                with open(icon_path, 'wb') as f:
                    f.write(icon.content)
            if not os.path.exists(icon_path) and gamedata['icon_url'] is not None:
                banner = LutrisClient.getBanner(gamedata['banner_url'])
                with open(banner_path, 'wb') as f:
                    f.write(banner.content)
            if not os.path.exists(info_path):
                with open(info_path, 'wb') as f:
                    json.dumps(gamedata, f)
        except:
            xbmc.log('{0}: Failed to fetch Artwork from Lutris.net'.format(addon_name), xbmc.LOGWARNING)

        # Get the local artwork
        game['icon'] = os.path.join(lutris_data, 'icons', game['slug'] + '.png')
        game['banner'] = os.path.join(lutris_data, 'banners', game['slug'] + '.jpg')
        game['platform'] = ""
        game['genre'] = []
        with open(info_path, 'r') as f:
            data = json.load(f)
            for platform in data['platforms']:
                game['platform'] += '{0},'.format(platform['name'])
            for genre in data['genres']:
                game['genre'].append(genre['name'])
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        li.setArt({'thumb': game['icon'], 'icon': game['icon'], 'banner': game['banner']})
        # Set info (title, platform, genres, publisher, developer, overview, year, gameclient) for the list item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        li.setInfo('game', {'title': game['name'],
                            'platform': game['platform'],
                            'genres': game['genres'],
                            'gameclient': game['runner']})
        # Set 'IsPlayable' property to 'true'. This is mandatory for playable items!
        li.setProperty('IsPlayable', 'true')
        # Create list to hold context meny items
        contextmenu = []
        # Append a info item to the context menu list
        contextmenu.append(('Information', 'xbmc.Action(Info)'))
        # Set the context menu from the items in the context menu list.
        # Replace the original items in the context menu.
        li.addContextMenuItems(contextmenu)
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.script.lutris/?action=play&id=74&name=A%20Story%20About%20My%20Uncle
        url = get_url(action='play', id=game['id'], name=game['name'])
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add the item to item list
        list_items.append((url, li, is_folder))
    # Add the list containing all game items to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItems(addon_handle, list_items)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(addon_handle)


def router(paramstring):
    """
    Router function that calls other functions depending on the provided paramstring.

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(urlparse.parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params['action'] == 'play':
        # Play a game from a provided URL.
        # Notify user that game is launching
        xbmcgui.Dialog().notification(addon_name, localized_string(30002).format(params['name']),
                                      xbmcgui.NOTIFICATION_INFO)
        Lutris.playGame(params['id'])
    else:
        list_games()

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
