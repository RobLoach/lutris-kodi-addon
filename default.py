# -*- coding: utf-8 -*-
# Module: default
# Author: ???
# Created on: ???
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

import json
import os
import sys
import urllib
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from subprocess import check_output
from distutils.spawn import find_executable

# Get the plugin url in plugin:// notation.
base_url = sys.argv[0]
# Get the plugin handle as an integer number.
addon_handle = int(sys.argv[1])
# Get the addon settings
addon_settings = xbmcaddon.Addon(id='script.lutris')
# Get the addon name from addon settings
addon_name = addon_settings.getAddonInfo('name')
# Get the localized string from addon settings
localized_string = addon_settings.getLocalizedString


def log(msg, level=xbmc.LOGDEBUG):
    """
    Output message to kodi.log file.

    :param msg: message to output
    :param level: debug levelxbmc. Values:
    xbmc.LOGDEBUG = 0
    xbmc.LOGERROR = 4
    xbmc.LOGFATAL = 6
    xbmc.LOGINFO = 1
    xbmc.LOGNONE = 7
    xbmc.LOGNOTICE = 2
    xbmc.LOGSEVERE = 5
    xbmc.LOGWARNING = 3
    """
    # Write error message to kodi.log
    log_message = u'{0}: {1}'.format(addon_name, msg, )
    xbmc.log(log_message, level)


def notify(msg):
    """
    Send  kodi dialog notification to the user.

    :param msg: Message to display
    :type kwargs: string
    """
    xbmcgui.Dialog().notification(addon_name, msg, xbmcgui.NOTIFICATION_INFO)


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument: value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: string
    """
    return '{0}?{1}'.format(base_url, urllib.urlencode(kwargs))


def lutris(args=None):
    """
    Get the path to the lutris executable and append optional command line arguments.

    note:: Possible arguments for the lutris executable are:
    -v, --version              Print the version of Lutris and exit
    -d, --debug                Show debug messages
    -i, --install              Install a game from a yml file
    -e, --exec                 Execute a program with the lutris runtime
    -l, --list-games           List all games in database
    -o, --installed            Only list installed games
    -s, --list-steam-games     List available Steam games
    --list-steam-folders       List all known Steam library folders
    -j, --json                 Display the list of games in JSON format
    --reinstall                Reinstall game
    --display=DISPLAY          X display to use

    :param args: arguments to append to the lutris command
    :type args: string
    :return: the path to the lutris executable with optional arguments
    :rtype: string
    """
    # Check if the user has specified a custom path to the lutris executable
    if addon_settings.getSetting('use_custom_path') == 'true':
        # Get the path from addon settings
        executable = addon_settings.getSetting('lutris_executable')
    else:
        # Find the path to the lutris executable
        executable = find_executable("lutris")
    # Print the excecutable path to the log
    log(executable, level=xbmc.LOGDEBUG)
    if args is not None:
        # Append command arguments to executable path
        executable = executable + args
    return executable


def get_games():
    """
    Get a list of installed games from lutris as a JSON object and convert it to a Python array.

    note::  JSON object returned from Lutris looks as follows:
    [
      {
        "id": 74,
        "slug": "a-story-about-my-uncle",
        "name": "A Story About My Uncle",
        "runner": "steam",
        "directory": ""
      },
      {
        ...
      }
    ]

    :return: list of installed games
    :rtype: list
    """
    try:
        # Get the list of games from Lutris as JSON
        cmd = lutris(' --list-games --json --installed')
        result = check_output(cmd, shell=True)
    except Exception as e:
        # Log error if list could not be found
        log(e, level=xbmc.LOGERROR)
    # Parse the list of games from JSON to a Python array.
    try:
        games = json.loads(result)
    except Exception as e:
        # Log error if JSON could not be opened
        log(e, level=xbmc.LOGERROR)
    return games


def convert_to_utf8(li):
    """
    Take a list containing nested dictionaries and encode the dictionary values to unicode.

    :param li: list of nested dicts
    :type li: list
    :return: list of nested dicts
    :rtype: list
    """
    for item in li:
        # Check if item is a list
        if isinstance(item, list):
            # Run the function recursely on the list
            convert_to_utf8(item)
        # Check if item is a dict
        elif isinstance(item, dict):
            # Iterate over the keys in the dict
            for key, value in item.iteritems():
                # Convert value to UTF8 and store to original key
                item[key] = unicode(value).encode('utf-8')
    return li


def list_games():
    """Create the list of games in the Kodi interface."""
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(addon_handle, 'My Lutris Collection')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(addon_handle, 'files')
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
    games = convert_to_utf8(get_games())
    # Iterate through the games
    for game in games:
        # Create a list item with a text label and a thumbnail image.
        li = xbmcgui.ListItem(label=game['name'])
        # Set info (title, platform, genres, publisher, developer, overview, year, gameclient) for the list item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        li.setInfo('game', {'title': game['name'], 'gameclient': game['runner']})
        # Expand the path to the users home folder
        home = os.path.expanduser('~')
        # Get the local artwork
        game['icon'] = os.path.join(home, '.local', 'share', 'icons', 'hicolor', '128x128', 'apps', 'lutris_' + game['slug'] + '.png')
        game['banner'] = os.path.join(home, '.local', 'share', 'lutris', 'banners', game['slug'] + '.jpg')
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        li.setArt({'thumb': game['icon'], 'icon': game['icon'], 'banner': game['banner']})
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


def play_game(id_, name):
    """
    Play a game by the provided id.

    :param id: fully-qualified game id
    :type path: string
    :param name: Fully qualified game name
    :type name: string
    """
    # Construct the launch command
    if name != 'Lutris':
        cmd = lutris(' lutris:rungameid/' + id_)
    else:
        cmd = lutris()
    # Stop playback if Kodi is playing any media
    if xbmc.Player().isPlaying():
        xbmc.Player().stop()
    # Notify user that game is launching
    notify(localized_string(30002).format(name))
    # Log lutris command to kodi.log
    log(cmd, level=xbmc.LOGDEBUG)
    # Launch Lutris
    os.system(cmd)


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
    print params
    if 'content_type' in params:
        list_games()
    elif params['action'] == 'play':
        # Play a game from a provided URL.
        play_game(params['id'], params['name'])
    else:
        # If the provided paramstring does not contain a supported action
        # we raise an exception. This helps to catch coding errors,
        # e.g. typos in action names.
        raise ValueError('Invalid paramstring: {0}!'.format(paramstring))

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
