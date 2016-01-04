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

# Discover what the user is doing
mode = args.get('mode', None)
if mode is None:
    addon = xbmcaddon.Addon('script.lutris')
    fanart = addon.getAddonInfo('fanart')

    # Add the Launch Lutris item
    title = language(30000)
    iconImage = os.path.join(settings.getAddonInfo('path'), 'icon.png')
    url = build_url({'mode': 'folder', 'foldername': title, 'slug': 'lutris'})
    li = xbmcgui.ListItem(title, iconImage=iconImage)
    li.setArt({'fanart': fanart})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    # Get a list of the games from Lutris
    args = settings.getSetting('lutris_executable') + ' --list-games --json'
    if settings.getSetting('installed'):
        args += ' --installed'
    result = subprocess.check_output(args, shell=True)

    games = []
    try:
        games = json.loads(result)
    except:
        print 'Cannot parse games json'
        print games

    totalItems = len(games)
    for game in games:
        # Filter out the unprintable Unicode characters
        name = filter(lambda x: x in string.printable, game['name'])
        slug = filter(lambda x: x in string.printable, game['slug'])
        runner = game['runner'] or ''
        if runner == '-':
            runner = ''

        # Construct the list item
        li = xbmcgui.ListItem(name, runner, iconImage=iconImage)
        li.setArt({
            'fanart': fanart
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
    lutris = settings.getSetting('lutris_executable')
    slug = args['slug'][0]
    cmd = lutris
    if slug != 'lutris':
        cmd = cmd + ' lutris:' + slug
    os.system(cmd)
