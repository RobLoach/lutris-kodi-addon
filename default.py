# Dependencies
import json
import os
import string
import subprocess
import sys
import urllib
import urlparse
import xbmcaddon
import xbmcgui
import xbmcplugin

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

def getLutrisExecutable():
    lutrisExecutable = settings.getSetting('lutris_executable')
    if lutrisExecutable == 'script.lutris':
        return os.path.join(settings.getAddonInfo('path'), 'lutris', 'bin', 'lutris')
    return lutrisExecutable

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

    # Get a list of the games from Lutris
    args = getLutrisExecutable() + ' --list-games --json'
    if settings.getSetting('installed') in [True, 'True', 'true', 1]:
        args = args + ' --installed'

    # Get the list of games from Lutris
    result = '[]'
    try:
        result = subprocess.check_output(args, shell=True)
    except:
        xbmcgui.Dialog().ok(
            'Lutris Not Found',
            '1. Install Lutris from http://lutris.com',
            '2. Select its executable location in the following settings')
        settings.openSettings()

    # Parse the list of games from JSON to a Python array.
    games = []
    try:
        games = json.loads(result)
    except:
        xbmcgui.Dialog().ok(
            'Lutris Result Malformed',
            '1. Make sure the Lutris executable path is correct',
            '2. Attempt launching and configuring it again')
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
        li = xbmcgui.ListItem(name, runner, iconImage=gameThumb)
        li.setArt({
            'fanart': fanart,
            'thumb': gameThumb,
            'banner': gameBanner,
            'poster': gameBanner
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
    lutris = getLutrisExecutable()
    slug = args['slug'][0]
    cmd = lutris
    if slug != 'lutris':
        cmd = cmd + ' lutris:' + slug
    os.system(cmd)
