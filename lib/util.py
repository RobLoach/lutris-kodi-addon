# -*- coding: utf-8 -*-
# Module: default
# Author: solbero
# Created on: 13.12.2020
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

# Imports
import xbmc
import xbmcaddon
import xbmcgui

# Globals
addon_id = xbmcaddon.Addon()
addon_name = addon_id.getAddonInfo('name')
localized_string = addon_id.getLocalizedString


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
    message = f"{addon_name}: {msg}"
    xbmc.log(message, lvl)


def notify_user(msg: str, heading: str = addon_name,
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


def show_error(msg: str):
    """Displays an error notification to the user.

    Args:
        msg (str): Message to display.

    """
    error_message = f"{msg}. {localized_string(30200)}."
    heading = f"{addon_name} {localized_string(30301)}"

    notify_user(error_message, heading, icon=xbmcgui.NOTIFICATION_ERROR)


def inhibit_idle_shutdown(bool_: bool):
    """Enables or disables the Kodi idle shutdown timer.

    Args:
        bool_ (bool): True for enable, False for disable.

    """
    xbmc.executebuiltin(f"InhibitIdleShutdown({str(bool_).lower()})")
    log(f"Inhibit idle shutdown is: {bool_}")


def stop_playback():
    """Stop playback if Kodi is playing any media. """
    if xbmc.Player().isPlaying():
        xbmc.Player().stop()
