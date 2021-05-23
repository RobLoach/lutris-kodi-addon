# -*- coding: utf-8 -*-
# Module: default
# Author: solbero
# Created on: 13.12.2020
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

# Imports
import functools
from typing import Any, Callable

import xbmc
import xbmcaddon
import xbmcgui

# Globals
_addon_id = xbmcaddon.Addon()
_addon_name = _addon_id.getAddonInfo('name')
_localized = _addon_id.getLocalizedString


def log(msg: str, lvl: int = 1):
    """Writes a message to the log.

    Message is prefixed with add-on name.

    Note:
        Severity level parameters:
            1 = LOGDEBUG
            2 = LOGINFO
            3 = LOGNOTICE
            4 = LOGWARNING
            5 = LOGERROR
            6 = LOGSEVERE
            7 = LOGFATAL
            8 = LOGNONE

    Args:
        msg (str): Message to write to kodi.log.
        lvl (int, optional): Severity level. Defaults to 1.
    """
    message = f"{_addon_name}: {msg}"
    xbmc.log(message, lvl)


def notify_user(msg: str, heading: str = _addon_name,
                icon=xbmcgui.NOTIFICATION_INFO):
    """Displays a notification to the user. Add-on name is added as a
    heading to the message.

    Note:
        Icon parameters:
            xbmcgui.NOTIFICATION_INFO
            xbmcgui.NOTIFICATION_WARNING
            xbmcgui.NOTIFICATION_ERROR

    Args:
        msg (str): Message to display.
        heading (str, optional): Heading to display with message.
            Defaults to '_addon_name'.
        icon (str, optional): Notification icon to follow message.
            Defaults to 'xbmcgui.NOTIFICATION_INFO'.
    """
    xbmcgui.Dialog().notification(heading, msg, icon)


def on_playback(func: Callable) -> Callable:
    """Decorator which performs pre and post operations on playback.

    Decorator which stops playback and suspends idle shutdown before
    calling decorated function. After function is finished enables
    idle shutdown.

    Args:
        func (Callable): Function to decorate.
    """
    @functools.wraps(func)
    def decorated(*args, **kwargs) -> Any:
        if xbmc.Player().isPlaying():
            xbmc.Player().stop()

        xbmc.executebuiltin('InhibitIdleShutdown(true)')

        response = func(*args, **kwargs)

        xbmc.executebuiltin('InhibitIdleShutdown(false)')

        return response

    return decorated
