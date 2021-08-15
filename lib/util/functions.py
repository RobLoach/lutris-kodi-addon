# -*- coding: utf-8 -*-
# Module: default
# Author: solbero
# Created on: 13.12.2020
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

# Imports
import functools
import os
import requests
import sys
from dataclasses import dataclass
from ast import literal_eval
from typing import Any, List, Callable, TypeVar, Union, cast

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

try:
    import StorageServer
except ImportError:
    import lib.util.storageserverdummy as StorageServer

# Type aliases
DecoratedType = TypeVar('DecoratedType', bound=Callable[..., Any])


# Functions
def get_localized_string(id: int) -> str:
    return _addon.getLocalizedString(id)


def log(msg: str, lvl: int = xbmc.LOGDEBUG):
    """Writes a message to the log.

    Message is prefixed with add-on name.

    Note:
        Severity level parameters:
            0 = xbmc.LOGDEBUG
            1 = xbmc.LOGINFO
            2 = xbmc.LOGNOTICE
            3 = xbmc.LOGWARNING
            4 = xbmc.LOGERROR
            5 = xbmc.LOGSEVERE
            6 = xbmc.LOGFATAL
            7 = xbmc.LOGNONE

    Args:
        msg (str): Message to write to kodi.log.
        lvl (int, optional): Severity level. Defaults to xbmc.LOGDEBUG.
    """
    message = f"{ADDON_NAME}: {msg}"
    xbmc.log(message, lvl)


def notify_user(msg: str, heading: str = ADDON_NAME,
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


def delete_cache():
    """Deletes all game data stored in Simple Plugin Cache"""
    storageserver = StorageServer.StorageServer(ADDON_NAME)
    storageserver.delete('%')

    log("Deleted games cache")


def download_file(url: str, folder: str, filename: str) -> str:
    folder_path = os.path.join(ADDON_DATA_FOLDER, folder)
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)

    file_path = os.path.join(folder_path, filename)
    request = requests.get(url)
    with open(file_path, 'wb') as file:
        file.write(request.content)

    return file_path


# Decorators
def on_playback(func: DecoratedType) -> DecoratedType:
    """Decorator which performs pre and post operations on playback.

    Decorator which stops playback and disables idle shutdown before
    calling decorated function. After function terminates enables
    idle shutdown again.

    Args:
        func (Callable): Function to decorate.

    Returns:
        decorated (Callable): Decorated function.
    """
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        if xbmc.Player().isPlaying():
            xbmc.Player().stop()
            log("Stopped Kodi playback before launching game")

        xbmc.executebuiltin('InhibitIdleShutdown(true)')
        log("Prevent the system to shutdown on idle before launching game")

        response = func(*args, **kwargs)

        xbmc.executebuiltin('InhibitIdleShutdown(false)')
        log("Allow the system to shutdown on idle after launching game")

        return response

    return cast(DecoratedType, decorated)


def use_cache(func: DecoratedType) -> DecoratedType:
    """Decorator which applies caching to passed function.

    Checks if function response is in the cache, if it is the cached respose
    is returned. If response is not in the cache or the cached response is
    stale, the function is called and its response is cached. If caching is
    disabled in the add-on settings the function response is returned
    without caching.

    Args:
        func (Callable): Function to decorate.

    Returns:
        decorated (Callable): Decorated function.
    """
    @functools.wraps(func)
    def decorated(*args, **kwargs) -> Any:


        storageserver = StorageServer.StorageServer(ADDON_NAME, CACHE_EXPIRE_HOURS)
        cache = storageserver.get(func.__name__)

        if ENABLE_CACHE and cache:
            response = literal_eval(cache)
            log(f"Got cache for function '{func.__name__}'")
        elif ENABLE_CACHE and not cache:
            response = func(*args, **kwargs)
            storageserver.set(func.__name__, repr(response))
            log(f"Set cache for function '{func.__name__}'")
        else:
            response = func(*args, **kwargs)
            log(f"Could not cache function '{func.__name__}'")

        return response

    return cast(DecoratedType, decorated)
