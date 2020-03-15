# -*- coding: utf-8 -*-
# Module: default
# Author: Rob Loach
# Created on: 28.12.2015
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

from __future__ import unicode_literals
import xbmc
import xbmcaddon
from subprocess import call
from distutils.spawn import find_executable

# Get the addon id
addon = xbmcaddon.Addon(id='script.lutris')
# Get the addon name
addon_name = addon.getAddonInfo('name')


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


def lutris():
    """
    Get the path to the Lutris executable

    :return: path to the Lutris executable
    :rtype: string
    """
    # Check if the user has specified a custom path in addon settings
    if addon.getSetting('custom_path') == 'true':
        # Get the custom path from addon settings
        path = addon.getSetting('executable').decode('utf-8')
    else:
        # Find the path to the lutris executable
        path = find_executable("lutris").decode('utf-8')
    # Log executable path to kodi.log
    log('Executable path is {}'.format(path))
    return path

cmd = lutris().encode('utf-8')
call([cmd])
