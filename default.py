# -*- coding: utf-8 -*-
# Module: default
# Author: Rob Loach
# Created on: 28.12.2015
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

from __future__ import unicode_literals
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
# Get the addon id
addon = xbmcaddon.Addon()
# Get the addon name
addon_name = addon.getAddonInfo('name')
# Get the localized strings
language = addon.getLocalizedString


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
    # Decode message to UTF8
    if isinstance(msg, str):
        msg = msg.decode('utf-8')
    # Write message to kodi.log
    log_message = '{0}: {1}'.format(addon_name, msg)
    xbmc.log(log_message.encode('utf-8'), level)


def notify(msg):
    """
    Display a kodi dialog notification dialog.

    :param msg: message to display
    :type msg: string
    """
    # Decode message to UTF8
    if isinstance(msg, str):
        msg = msg.decode('utf-8')
    # Display message in Kodi UI
    xbmcgui.Dialog().notification(addon_name, msg.encode('utf-8'))


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of
    keyword arguments.

    :param kwargs: "argument: value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: string
    """
    return '{0}?{1}'.format(base_url, urllib.urlencode(kwargs))


def inhibit_shutdown(bool):
    """
    Enable or disable the built in kodi idle shutdown timer.

    :param bool: true or false boolean
    :type bool: bool
    """
    # Convert bool argument to lowercase string
    str_bool = str(bool).lower
    # Send bool value to Kodi
    xbmc.executebuiltin('InhibitIdleShutdown({0})'.format(str_bool))


def lutris(args=None):
    """
    Get the path to the lutris executable and append optional
    command line arguments.

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

    :param args: arguments to append to the lutris executable path
    :type args: string
    :return: path to the lutris executable with optional arguments
    :rtype: string
    """
    # Check if the user has specified a custom path in addon settings
    if addon.getSetting('use_custom_path') == 'true':
        # Get the custom path from addon settings
        path = addon.getSetting('lutris_executable').decode('utf-8')
    else:
        # Find the path to the lutris executable
        path = find_executable("lutris").decode('utf-8')
    # Check if arguments are passed to the function
    if args is not None:
        # Append command arguments to executable path
        cmd = path + args
    else:
        # Set command to executable path
        cmd = path
    # Log executable path to kodi.log
    log('Executable path is {}'.format(path))
    return cmd


def get_games():
    """
    Fetch a list of managed games from lutris as a JSON object and convert
    it to a Python array.

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
    # Arguments to fetch games as a JSON object
    args = ' --list-games --json'
    # Check add on settings if only installed games should be fetched
    if addon.getSetting('installed') == 'true':
        args = args + ' --installed'
    # Get the list of games from Lutris as JSON
    cmd = lutris(args)
    result = check_output(cmd, shell=True)
    # Parse the list of games from JSON to a Python array.
    response = json.loads(result)
    # Log Python array to kodi.log
    log('JSON output is {0}'.format(response))
    return response


def list_games():
    """Create a list of games in the Kodi interface."""
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(addon_handle, language(30000))
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(addon_handle, 'games')
    # Create list to hold list items
    list_items = []
    # Get list of games from lutris
    games = get_games()
    # Iterate through the list of games
    for game in games:
        # Check if game is installed
        if game['runner'] is None:
            # Append not installed to game name
            game['name'] = '{0} (not installed)'.format(game['name'])
        # Create a list item with a label.
        li = xbmcgui.ListItem(label=game['name'])
        # Set 'IsPlayable' property to 'true'. This is mandatory for playable items!
        li.setProperty('IsPlayable', 'true')
        # Set info (title, platform, genres, publisher, developer, overview,
        # year, gameclient) for the list item.
        li.setInfo('game', {'title': game['name'], 'gameclient': game['runner']})
        # Expand the path to the user's home folder
        home = os.path.expanduser('~').decode('utf-8')
        # Get the local game artwork
        game['icon'] = os.path.join(home, '.local', 'share', 'icons', 'hicolor', '128x128', 'apps', 'lutris_' + game['slug'] + '.png')
        game['banner'] = os.path.join(home, '.local', 'share', 'lutris', 'banners', game['slug'] + '.jpg')
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for
        # the list item.
        li.setArt({'thumb': game['icon'], 'icon': game['icon'], 'banner': game['banner']})
        # Create list to hold context menu items
        context_menu = []
        # Append infomation item to the context menu list
        context_menu.append((language(30202), 'Action(Info)'))
        # Check if game is not installed
        if game['runner'] is None:
            # Append install item to the context menu list
            context_menu.append((language(30201), 'RunPlugin({0})'.format(get_url(action='install', id=game['id'], slug=game['slug'], name=game['name'].encode('utf8')))))
        else:
            # Append reinstall item to the context menu list
            context_menu.append((language(30200), 'RunPlugin({0})'.format(get_url(action='reinstall', id=game['id'], slug=game['slug'], name=game['name'].encode('utf8')))))
        # Set context menu from tuples in context menu list
        li.addContextMenuItems(context_menu)
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.script.lutris/?action=play&id=74&slug=a-story-about-my-uncle&name=A%20Story%20About%20My%20Uncle
        url = get_url(action='play', id=game['id'], slug=game['slug'], name=game['name'].encode('utf8'))
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add the item to item list
        list_items.append((url, li, is_folder))
    # Add the list containing all game items to the Kodi virtual
    # folder listing.
    xbmcplugin.addDirectoryItems(addon_handle, list_items)
    # Add a sort method for the virtual folder items
    # (alphabetically, ignore articles).
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(addon_handle)


def launch(action, id_=None, slug=None):
    """
    Play, install or reinstall a game.

    :param id: lutris game id
    :type path: string
    """
    # Check if action is playable
    if action == 'play':
        # Construct play command
        cmd = lutris(' lutris:rungameid/' + id_)
    # Check if action is install
    elif action == 'install' or action == 'reinstall':
        # Construct install and reinstall command
        cmd = lutris(' lutris:' + slug + ' --reinstall')
    elif action == 'lutris':
        # Construct open application command
        cmd = lutris()
    else:
        # If the provided action does not contain a supported action
        # we raise an exception.
        raise ValueError('Invalid action: {0}'.format(action))
    # Stop playback if Kodi is playing any media
    if xbmc.Player().isPlaying():
        xbmc.Player().stop()
    # Log launch command to kodi.log
    log('Launch command is {0}'.format(cmd))
    # Disable the idle shutdown timer
    inhibit_shutdown(True)
    # Launch lutris with command
    try:
        os.system(cmd.encode('utf-8'))
    except:
        # Notify the user that executable was not found
        notify(language('Lutris not found'))
        # Log error to kodi.log
        log('Executable not found. Make sure the path to the executable is correct in the addon settings.', level=xbmc.LOGERROR)
    # Enable the idle shutdown timer
    inhibit_shutdown(False)


def router(paramstring):
    """
    Router function that calls other functions depending on the provided paramstring.

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(urlparse.parse_qsl(paramstring))
    if params:
        if 'action' in params:
            if params['action'] == 'play' or params['action'] == 'lutris':
                notify(language(30300).format(params['name']))
            elif params['action'] == 'install':
                notify(language(30301).format(params['name']))
            elif params['action'] == 'reinstall':
                notify(language(30302).format(params['name']))
            # Do an action (play, install, reinstall) on the selected game
            launch(params['action'], params['id'], params['slug'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}'.format(paramstring))
    else:
        # Display the list of games from lutris
        list_games()

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
