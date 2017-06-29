# Dependencies
import json
import os
import string
import subprocess
import sys
import urllib
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from distutils.spawn import find_executable

# Globals
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
settings = xbmcaddon.Addon(id='script.lutris')
language = settings.getLocalizedString
xbmcplugin.setContent(addon_handle, 'files')

# Construct a URL for the Kodi navigation
def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

# Discover what the user is doing
mode = args.get('mode', None)
if mode is None:
    addon = xbmcaddon.Addon('script.lutris')
    fanart = addon.getAddonInfo('fanart')
    home = os.path.expanduser('~')

    # Add the Launch Lutris item
    title = language(30000)
    iconImage = os.path.join(settings.getAddonInfo('path'), 'icon.png')
    url = build_url({'mode': 'folder', 'foldername': title, 'slug': 'lutris'})
    li = xbmcgui.ListItem(title, iconImage=iconImage)
    li.setArt({'fanart': fanart})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, totalItems=2)

    # Get the path to the Lutris executable
    if settings.getSetting('use_custom_path') in [True, 'True', 'true', 1]:
        executable = settings.getSetting('lutris_executable')
    else:
        try:
            executable = find_executable("lutris")
        except:
            xbmcgui.Dialog().ok(
                'Lutris Not Found',
                '1. Install Lutris from http://lutris.com',
                '2. If Lutris is installed and the problem persists set a custom path to the executable in the add-on settings')

    # Append arguments to executable path
    args = executable + ' --list-games --json'
    if settings.getSetting('installed') in [True, 'True', 'true', 1]:
        args = args + ' --installed'

    # Get the list of games from Lutris
    result = '[]'
    try:
        result = subprocess.check_output(args, shell=True)
    except:
        xbmcgui.Dialog().ok(
            'Lutris Not Found',
            '1. Make sure the Lutris executable path is correct')
        settings.openSettings()

    # Parse the list of games from JSON to a Python array.
    games = []
    try:
        games = json.loads(result)
    except:
        xbmcgui.Dialog().ok(
            'Lutris Result Malformed',
            '1. Make sure the Lutris executable path is correct',
            '2. Attempt configuring and launching the add-on again')
        settings.openSettings()

    totalItems = len(games)
    for game in games:
        # Filter out the unprintable Unicode characters
        name = filter(lambda x: x in string.printable, game['name'])
        slug = filter(lambda x: x in string.printable, game['slug'])
        runner = game['runner'] or ''
        if runner == '-':
            runner = ''

        # Construct the list item
        gameThumb = os.path.join(home, '.local', 'share', 'icons', 'hicolor', '32x32', 'apps', 'lutris_' + slug + '.png')
        gameBanner = os.path.join(home, '.local', 'share', 'lutris', 'banners', slug + '.jpg')
        li = xbmcgui.ListItem(name, runner, iconImage=gameBanner)
        li.setArt({
            'fanart': fanart,
            'thumb': gameBanner,
            'banner': gameBanner,
            'poster': gameBanner,
            'landscape': gameBanner
        })
        li.setProperty('Runner', runner)

        # Add the contextual menu
        commands = []
        if runner:
            commands.append((language(30200) % (runner), 'RunPlugin(%s?mode=folder&slug=%s)' % (sys.argv[0], slug + ' --reinstall')))
        li.addContextMenuItems(commands)

        # Add the list item into the directory listing
        url = build_url({'mode': 'folder', 'foldername': name, 'slug': slug})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, totalItems=totalItems)

    # Finished the list
    xbmcplugin.endOfDirectory(addon_handle)

# Launch
elif mode[0] == 'folder':
    lutris = executable
    slug = args['slug'][0]
    cmd = lutris
    if slug != 'lutris':
        cmd = cmd + ' lutris:rungame/' + slug
    if xbmc.Player().isPlaying() == True:
        xbmc.Player().stop()
    os.system(cmd)
