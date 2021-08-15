# -*- coding: utf-8 -*-
# Module: default
# Author: solbero
# Created on: 15.08.2021
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

# Imports
import os
import sys

import xbmcaddon
import xbmcvfs

# Globals
_addon = xbmcaddon.Addon()

# Add-on constants
ADDON_NAME = _addon.getAddonInfo('name')
ADDON_ID = _addon.getAddonInfo('id')
ADDON_HANDLE = int(sys.argv[1])
ADDON_DATA_FOLDER = os.path.join(xbmcvfs.translatePath('special://userdata'), 'addon_data', ADDON_ID)

# Add-on settings
ENABLE_CUSTOM_PATH = _addon.getSettingBool('enable_custom_path')
CUSTOM_PATH = _addon.getSettingString('custom_path')
ENABLE_CACHE = _addon.getSettingBool('enable_cache')
CACHE_EXPIRE_HOURS = _addon.getSettingInt('cache_expire_hours')
