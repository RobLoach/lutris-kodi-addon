# -*- coding: utf-8 -*-
# Module: default
# Author: solbero
# Created on: 13.12.2020
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

# Imports
import functools
from ast import literal_eval
from typing import Any, Callable

import xbmc
import xbmcaddon
import xbmcgui

try:
    import StorageServer
except ImportError:
    import lib.storageserverdummy as StorageServer


# Globals
_addon = xbmcaddon.Addon()
_addon_name = _addon.getAddonInfo('name')
_cache_expire_hours = _addon.getSettingInt('cache_expire_hours')
_cache = StorageServer.StorageServer(_addon_name, _cache_expire_hours)

# Type aliases
DecoratedType = TypeVar('DecoratedType', bound=Callable[..., Any])


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

        xbmc.executebuiltin('InhibitIdleShutdown(true)')

        response = func(*args, **kwargs)

        xbmc.executebuiltin('InhibitIdleShutdown(false)')

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
        enable_cache = _addon.getSettingBool('enable_cache')
        cache = _cache.get(func.__name__)

        if enable_cache and cache:
            response = literal_eval(cache)
            log(f"Got cache for function '{func.__name__}'")
        elif enable_cache and not cache:
            response = func(*args, **kwargs)
            _cache.set(func.__name__, repr(response))
            log(f"Set cache for function '{func.__name__}'")
        else:
            response = func(*args, **kwargs)
            log(f"Could not cache function '{func.__name__}'")

        return response

    return cast(DecoratedType, decorated)


def delete_cache():
    """Deletes all add-on data stored in the cache"""
    _cache.delete('%')

    log("Deleted cache")
