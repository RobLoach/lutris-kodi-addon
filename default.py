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

# Set the plugin content
xbmcplugin.setContent(addon_handle, 'games')


# Construct a URL for the Kodi navigation
def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


# Find the path to the Lutris executable
def lutris_executable():
    if settings.getSetting('use_custom_path') == 'true':
        path = settings.getSetting('lutris_executable')
    else:
        path = find_executable("lutris")
    return path

# Discover what the user is doing
mode = args.get('mode', None)

# Construct the folder listing in Kodi
if mode is None:
    home = os.path.expanduser('~')

    # Add the Launch Lutris item
    title = 'Lutris'
    fanart = settings.getAddonInfo('fanart')
    iconImage = settings.getAddonInfo('icon')

    url = build_url({'mode': 'folder', 'foldername': title, 'slug': 'lutris'})
    li = xbmcgui.ListItem(title, iconImage=iconImage)
    li.setArt({
        'fanart': fanart,
        'thumb': iconImage
    })
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, totalItems=2)

    # Append arguments to executable path
    try:
        args = lutris_executable() + ' --list-games --json'
    except:
        xbmcgui.Dialog().ok(
            language(30300),
            language(30301),
            language(30302))

    if settings.getSetting('installed') == 'true':
        args = args + ' --installed'

    # Get the list of games from Lutris
    result = '[]'
    try:
        result = subprocess.check_output(args, shell=True)
    except:
        xbmcgui.Dialog().ok(
            language(30300),
            language(30303))
        settings.openSettings()

    # Parse the list of games from JSON to a Python array.
    games = []
    try:
        games = json.loads(result)
    except:
        xbmcgui.Dialog().ok(
            language(30304),
            language(30303),
            language(30305))
        settings.openSettings()

    totalItems = len(games)
    for game in games:
        # Filter out the unprintable Unicode characters
        name = filter(lambda x: x in string.printable, game['name'])
        slug = filter(lambda x: x in string.printable, game['slug'])
        game_id = game['id']
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
            commands.append((language(30200) % (runner), 'RunPlugin(%s?mode=folder&id=%d&slug=%s&gamename=%s)' % (base_url, game_id, slug + ' --reinstall', name)))
        li.addContextMenuItems(commands)

        # Add the list item into the directory listing
        url = build_url({'mode': 'folder', 'foldername': name, 'id': game_id, 'slug': slug, 'gamename': name})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, totalItems=totalItems)

        # Add sort method for list items
        xbmcplugin.addSortMethod(handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

    # Finished the list
    xbmcplugin.endOfDirectory(addon_handle)


# Launch
elif mode[0] == 'folder':
    cmd = lutris_executable()
    slug = args['slug'][0]
    game_id = args['id'][0]

    # Display a notification to let the user know the game is launching.
    game_name = filter(lambda x: x in string.printable, args['gamename'][0])
    addon_name = settings.getAddonInfo('name')

    xbmcgui.Dialog().notification(addon_name, language(30002) % (game_name), settings.getAddonInfo('icon'))

    # Construct the launch command
    if slug != 'lutris':
        cmd = cmd + ' lutris:rungameid/' + game_id

    # Stop playback if Kodi is playing any media
    if xbmc.Player().isPlaying():
        xbmc.Player().stop()

    # Get Users shutdowntimer value and save it so we can reset it to users value after the game has been quitted
    dpmssetting = json.loads(xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.getSettingValue", "params" : {"setting": "powermanagement.shutdowntime"} }'))

    # Disable Shutdowntimer (Set Value to 0)
    xbmcsetting = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.SetSettingValue", "params" : {"setting": "powermanagement.shutdowntime", "value": 0} }')

    # Launch Lutris
    os.system(cmd)

    # Reset shutdowntimer to users value
    xbmcsetting = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.SetSettingValue", "params" : {"setting": "powermanagement.shutdowntime", "value": ' + str(dpmssetting['result']['value']) + '} }')
