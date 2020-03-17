# -*- coding: utf-8 -*-
# Module: default
# Author: Rob Loach
# Created on: 28.12.2015
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

from __future__ import unicode_literals
import xbmcaddon
from subprocess import call
from distutils.spawn import find_executable

# Get the addon id
addon = xbmcaddon.Addon('script.lutris')


def get_path():
    """
    Get the path to the Lutris executable.

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
    # Log lutris executable path to kodi.log
    return path


if __name__ == '__main__':
    # Add the path to the lutris executable to the command list
    cmd = get_path()
    # Launch lutris with command. Subprocess.call waits for the game
    # to finish before continuing
    call(cmd)
