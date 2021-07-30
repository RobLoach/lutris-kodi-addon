# -*- coding: utf-8 -*-
# Module: default
# Author: solbero
# Created on: 13.12.2020
# License: GPL v.2 https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

# Imports
import datetime
import os
import requests_cache
import urllib.parse
from typing import Dict, Iterator, List, Tuple, Union

import xbmc
import xbmcaddon

# Constants
BASE_URL: str = 'https://api.thegamesdb.net/'
API_KEY: str = 'bfaf5ca817b0a117b12a7981424e6e4d1442227c39942e691f2d514ddfbcc333'

# Globals
_addon = xbmcaddon.Addon()
_addon_name = _addon.getAddonInfo('name')
_userdata_folder = xbmc.translatePath('special://userdata')
_addon_data_folder = os.path.join(_userdata_folder, 'addon_data', _addon_name)
_session = requests_cache.CachedSession(_addon_data_folder, ExpirationTime=datetime.timedelta(weeks=4))

# Type aliases
JSONAble = Union[str, int, float, bool, None]
JSONDict = Dict[JSONAble, Union[JSONAble, List[dict]]]
JSONList = List[JSONDict]
JSON = Union[JSONList, JSONDict]

GameID = Union[int, str]
PlatformID = Union[int, str]
GenreID = Union[int, str]
DeveloperID = Union[int, str]
PublisherID = Union[int, str]

GameName = str
PlatformName = str

GameInfo = JSONDict
PlatformInfo = JSONDict
GenreInfo = JSONDict
DeveloperInfo = JSONDict
PublisherInfo = JSONDict
ImageInfo = JSONDict

ImageType = str
ImageBaseURL = Dict[str, str]


def get_games_by_game_id(game_id: Union[GameID, List[GameID]],
                         fields: Union[str, List[str], None] = None) -> List[GameInfo]:
    """Gets game information from TheGamesDB (TGDB).

    Args:
        game_id (Union[GameID, List[GameID]): A GameID or list of GameIDs to request TGDB for information.
        fields (Union[str, List[str], None], optional): Include additional information fields in request.
    Raises:
        TypeError: Argument 'game_id' is not an int or list of int.
        ValueError: Argument 'fields' must be 'players', 'publishers', 'genres', 'overview', 'last_updated',
        'rating', 'platform', 'coop', 'youtube', 'os', 'processor', 'ram', 'hdd', 'video', 'sound',
        'alternates'.
        TypeError: Argument 'fields' must be string or list of string.

    Returns:
        List[GameInfo]: Returns a list of GameInfo.

        GameInfo is a JSONdict with keys 'id', 'game_title', 'release_date', 'platform', 'region_id', 'country_id'
        and 'developers'.
    """
    endpoint_url = '/v1/Games/ByGameID'
    valid_fields = ('players', 'publishers', 'genres', 'overview', 'last_updated', 'rating', 'platform', 'coop',
                    'youtube', 'os', 'processor', 'ram', 'hdd', 'video', 'sound', 'alternates')

    if isinstance(game_id, int):
        game_id_string = str(game_id)
    elif isinstance(game_id, list):
        game_id_string = ','.join(str(item) for item in game_id)
    else:
        raise TypeError("argument 'game_id' must be an int or list of int")

    if fields is not None and not any(entry in fields for entry in valid_fields):
        raise ValueError("argument 'fields' must be 'players', 'publishers', 'genres', 'overview', 'last_updated', \
                         'rating', 'platform', 'coop', 'youtube', 'os', 'processor', 'ram', 'hdd', 'video', 'sound', \
                         'alternates'")

    if fields is None:
        fields_string = ''
    elif isinstance(fields, str):
        fields_string = fields
    elif isinstance(fields, list):
        fields_string = ','.join(fields)
    else:
        raise TypeError("argument 'fields' must be string or list of string")

    params = {'id': game_id_string,
              'fields': fields_string}

    response_data = _request(endpoint_url, params)

    games = []
    for page in response_data:
        if isinstance(page['games'], list):
            games.extend(page['games'])

    return games


def get_games_by_game_name(game_name: GameName,
                           platform_id: Union[PlatformID, List[PlatformID], None] = None,
                           fields: Union[str, List[str], None] = None) -> List[GameInfo]:
    """Get game information from TheGamesDB (TGDB).

    Args:
        game_name (GameName): GameName to request the TGDB for information.
        platform_id Union[PlatformID, List[PlatformID], None], optional): Filter request by PlatformID. Defaults to
        None.
        fields (Union[str, List[str], None], optional): Include additional information fields in request.
    Raises:
        TypeError: Argument 'game_name' is not a str.
        TypeError: Argument 'platform_id' is not an int or list of int.
        ValueError: Argument 'fields' must be 'players', 'publishers', 'genres', 'overview', 'last_updated',
        'rating', 'platform', 'coop', 'youtube', 'os', 'processor', 'ram', 'hdd', 'video', 'sound',
        'alternates'.
        TypeError: Argument 'fields' must be string or list of string.

    Returns:
        List[GameInfo]: Returns a list of GameInfo.

        GameInfo is a JSONdict with keys 'id', 'game_title', 'release_date', 'platform', 'region_id', 'country_id'
        and 'developers'.
    """
    endpoint_url = '/v1.1/Games/ByGameName'
    valid_fields = ('players', 'publishers', 'genres', 'overview', 'last_updated', 'rating', 'platform', 'coop',
                    'youtube', 'os', 'processor', 'ram', 'hdd', 'video', 'sound', 'alternates')

    if isinstance(game_name, str):
        game_name_string = game_name
    else:
        raise TypeError("argument 'game_name' must be a str")

    if platform_id is None:
        platform_id_string = platform_id
    elif isinstance(platform_id, int):
        platform_id_string = str(platform_id)
    elif isinstance(platform_id, list):
        platform_id_string = ','.join(str(item) for item in platform_id)
    else:
        raise TypeError("argument 'platform_id' must be an int or list of int")

    if fields is not None and not any(entry in fields for entry in valid_fields):
        raise ValueError("argument 'fields' must be 'players', 'publishers', 'genres', 'overview', 'last_updated', \
                         'rating', 'platform', 'coop', 'youtube', 'os', 'processor', 'ram', 'hdd', 'video', 'sound', \
                         'alternates'")

    if fields is None:
        fields_string = ''
    elif isinstance(fields, str):
        fields_string = fields
    elif isinstance(fields, list):
        fields_string = ','.join(fields)
    else:
        raise TypeError("argument 'fields' must be string or list of string")

    params = {'name': game_name_string,
              'filter[platform]': platform_id_string,
              'fields': fields_string}

    response_data = _request(endpoint_url, params)

    games = []
    for page in response_data:
        if isinstance(page['games'], list):
            games.extend(page['games'])

    return games


def get_games_images(game_id: Union[GameID, List[GameID]],
                     image_type_filter: Union[ImageType, List[ImageType], None] = None)\
        -> Tuple[ImageBaseURL, Dict[GameID, List[ImageInfo]]]:
    """Gets game images from TheGamesDB (TGDB).

    Args:
        game_id (Union[GameID, List[GameID]]): A GameID or list of GameIDs to request TGDB for game images.
        image_type_filter (Union[ImageType, List[ImageType], None], optional): Filter request by ImageType, valid
        image types are 'fanart', 'banner', 'boxart', 'screenshot', 'clearlogo' and 'titlescreen'. Defaults to None.

    Raises:
        TypeError: Argument 'game_id' must be an int or list of int.
        ValueError: Argument 'image_type_filter' must be 'fanart', 'banner', 'boxart', 'screenshot', 'clearlogo'
                        and 'titlescreen'.
        TypeError: Argument 'image_type_filter' must be string or list of string.

    Returns:
        Tuple[ImageBaseURL, Dict[GameID, List[ImageInfo]]]: Returns a tuple with ImageBaseURL and
        Dict[GameID, List[ImageInfo]].

        ImageBaseURL is a JSONdict with keys 'original', 'small', 'thumb', 'cropped_center_thumb', 'medium'
        and 'large'.

        ImageInfo is a JSONdict with keys 'id', 'type', 'filename' and 'resolution'.
    """
    endpoint_url = '/v1/Games/Images'
    valid_image_types = ('fanart', 'banner', 'boxart', 'screenshot', 'clearlogo', 'titlescreen')

    if isinstance(game_id, int):
        game_id_string = str(game_id)
    elif isinstance(game_id, list):
        game_id_string = ','.join(str(item) for item in game_id)
    else:
        raise TypeError("argument 'game_id' must be an int or list of int")

    if image_type_filter is not None and not any(entry in image_type_filter for entry in valid_image_types):
        raise ValueError("argument 'image_type_filter' must be 'fanart', 'banner', 'boxart', 'screenshot', \
                         'clearlogo', 'titlescreen'")

    if image_type_filter is None:
        image_type_filter_string = ''
    elif isinstance(image_type_filter, str):
        image_type_filter_string = image_type_filter
    elif isinstance(image_type_filter, list):
        image_type_filter_string = ','.join(image_type_filter)
    else:
        raise TypeError("argument 'image_type_filter' must be string or list of string")

    params = {'games_id': game_id_string,
              'filter[type]': image_type_filter_string}

    response_data = _request(endpoint_url, params)

    base_url = {}
    game_images = {}
    for page in response_data:
        if isinstance(page['base_url'], dict):
            base_url.update(page['base_url'])
        if isinstance(page['images'], dict):
            game_images.update(page['images'])

    return base_url, game_images


def get_platforms(self) -> Dict[PlatformID, PlatformInfo]:
    """Gets platform information from TheGamesDB (TGDB).

    Returns:
        Dict[PlatformID, PlatformInfo]: Returns a dict with pairs of 'PlatformID: PlatformInfo'.

        PlatformInfo is a JSONdict with keys 'id', 'name' and 'alias'.
    """
    endpoint_url = '/v1/Platforms'

    response_data = _request(endpoint_url)

    platforms = {}
    for page in response_data:
        if isinstance(page['platforms'], dict):
            platforms.update(page['platforms'])

    return platforms


def get_platforms_by_platform_id(platform_id: Union[PlatformID, List[PlatformID]])\
        -> Dict[PlatformID, PlatformInfo]:
    """Gets platform information from TheGamesDB (TGDB).

    Args:
        platform_id (Union[PlatformID, List[PlatformID]]): PlatformID to request the TGDB for information.

    Raises:
        TypeError: Argument 'platform_id' must be an int or list of int

    Returns:
        Dict[PlatformID, PlatformInfo]: Returns a dict with pairs of 'PlatformID: PlatformInfo'.

        PlatformInfo is a JSONdict with keys 'id', 'name' and 'alias'.
    """
    endpoint_url = '/v1/Platforms/ByPlatformID'

    if isinstance(platform_id, int):
        platform_id_string = str(platform_id)
    elif isinstance(platform_id, list):
        platform_id_string = ','.join(str(item) for item in platform_id)
    else:
        raise TypeError("argument 'platform_id' must be an int or list of int")

    params = {'id': platform_id_string}

    response_data = _request(endpoint_url, params)

    platforms = {}
    for page in response_data:
        if isinstance(page['platforms'], dict):
            platforms.update(page['platforms'])

    return platforms


def get_platforms_by_platform_name(platform_name: PlatformName) -> List[PlatformInfo]:
    """Gets platform information from TheGamesDB (TGDB).

    Args:
        platform_name (PlatformName): PlatformName to request the TGDB for information.

    Raises:
        TypeError: Argument 'platform_name' must be a str.

    Returns:
        List[PlatformInfo]: Returns a list of PlatformInfo.

        PlatformInfo is a JSONdict with keys 'id', 'name' and 'alias'.
    """
    endpoint_url = '/v1/Platforms/ByPlatformName'

    if isinstance(platform_name, str):
        platform_name_string = str(platform_name)
    else:
        raise TypeError("argument 'platform_name' must be a str")

    params = {'name': platform_name_string}

    response_data = _request(endpoint_url, params)

    platforms = []
    for page in response_data:
        if isinstance(page['platforms'], list):
            platforms.extend(page['platforms'])

    return platforms


def get_platforms_images(platform_id: Union[PlatformID, List[PlatformID]],
                         image_type_filter: Union[ImageType, List[ImageType], None] = None)\
        -> Tuple[ImageBaseURL, Dict[PlatformID, List[ImageInfo]]]:
    """Gets game images from TheGamesDB (TGDB).

    Args:
        platform_id (Union[PlatformID, List[PlatformID]): A PlatformID or list of PlatformIDs to request TGDB for
        platform images.
        image_type_filter (Union[ImageType, List[ImageType], None], optional): Filter request by ImageType, valid
        image types are 'fanart', 'banner' and 'boxart'. Defaults to None.

    Raises:
        TypeError: Argument 'platform_id' must be an int or list of int.
        ValueError: Argument 'image_type_filter' must be 'fanart', 'banner' and 'boxart'.
        TypeError: Argument 'image_type_filter' must be string or list of string.

    Returns:
        Tuple[ImageBaseURL, Dict[PlatformID, List[ImageInfo]]]: Returns a tuple with ImageBaseURL and
        Dict[PlatformID, List[ImageInfo]].

        ImageBaseURL is a JSONdict with keys 'original', 'small', 'thumb', 'cropped_center_thumb', 'medium'
        and 'large'.

        ImageInfo is a JSONdict with keys 'id', 'type', 'filename' and 'resolution'.
    """
    endpoint_url = '/v1/Platforms/Images'
    valid_image_types = ('fanart', 'banner', 'boxart')

    if isinstance(platform_id, int):
        platform_id_string = str(platform_id)
    elif isinstance(platform_id, list):
        platform_id_string = ','.join(str(item) for item in platform_id)
    else:
        raise TypeError("argument 'platform_id' must be int or list of int")

    if image_type_filter is not None and not any(image in image_type_filter for image in valid_image_types):
        raise ValueError("argument 'image_type_filter' must be 'fanart', 'banner', 'boxart'")

    if image_type_filter is None:
        image_type_filter_string = ''
    elif isinstance(image_type_filter, str):
        image_type_filter_string = image_type_filter
    elif isinstance(image_type_filter, list):
        image_type_filter_string = ','.join(image_type_filter)
    else:
        raise TypeError("argument 'image_type_filter' must be str or list of string")

    params = {'platforms_id': platform_id_string,
              'filter[type]': image_type_filter_string}

    response_data = _request(endpoint_url, params)

    base_url = {}
    platforms_images = {}
    for page in response_data:
        if isinstance(page['base_url'], dict):
            base_url.update(page['base_url'])
        if isinstance(page['images'], dict):
            platforms_images.update(page['images'])

    return base_url, platforms_images


def get_genres(self) -> Dict[GenreID, GenreInfo]:
    """Gets genre information from TheGamesDB (TGDB).

    Returns:
        Dict[GenreID, GenreInfo]: Returns a dict with pairs of 'GenreID: GenreInfo'.

        GenreInfo is a JSONdict with keys 'id' and 'name'.
    """
    endpoint_url = '/v1/Genres'

    response_data = _request(endpoint_url)

    genres = {}
    for page in response_data:
        if isinstance(page['genres'], dict):
            genres.update(page['genres'])

    return genres


def get_developers(self) -> Dict[DeveloperID, DeveloperInfo]:
    """Gets developer information from TheGamesDB (TGDB).

    Returns:
        Dict[DeveloperID, DeveloperInfo]: Returns a dict with pairs of 'DeveloperID: DeveloperInfo'.

        DeveloperInfo is a JSONdict with keys 'id' and 'name'.
    """
    endpoint_url = '/v1/Developers'

    response_data = _request(endpoint_url)

    developers = {}
    for page in response_data:
        if isinstance(page['developers'], dict):
            developers.update(page['developers'])

    return developers


def get_publishers(self) -> Dict[PublisherID, PublisherInfo]:
    """Gets publisher information from TheGamesDB (TGDB).

    Returns:
        Dict[PublisherID, PublisherInfo]: Returns a dict with pairs of 'PublisherID: PublisherInfo'.

        PublisherInfo is a JSONdict with keys 'id' and 'name'.
    """
    endpoint_url = '/v1/Publishers'

    response_data = _request(endpoint_url)

    publishers = {}
    for page in response_data:
        if isinstance(page['publishers'], dict):
            publishers.update(page['publishers'])

    return publishers


def _request(endpoint_url: str, params: Union[Dict[str, str], None] = None) -> Iterator[JSONDict]:
    """Base function to request data from TheGamesDB (TGDB).

    Args:
        endpoint_url (str): A valid TGDB endpoint
        params (Union[Dict[str, str], None], optional): Params to send with request. Defaults to None

    Raises:
        ValueError: Argument 'params' must be a dict

    Yields:
        Iterator[JSONDict]: Parsed response from TGDB. Only value of key 'data' from response is returned.
    """
    url = urllib.parse.urljoin(BASE_URL, endpoint_url)

    if params is None:
        payload = {'apikey': API_KEY}
    elif isinstance(params, dict):
        payload = {**{'apikey': API_KEY}, **params}
    else:
        raise ValueError("argument 'params' must be a dict")

    response = _session.get(url, params=payload)
    response.raise_for_status()
    parsed_response = response.json()

    yield parsed_response['data']

    if 'pages' in parsed_response:
        next_url = parsed_response['pages']['next']

        while next_url:
            response = _session.get(next_url)
            response.raise_for_status()
            parsed_response = response.json()
            next_url = parsed_response['pages']['next']

            yield parsed_response['data']


print(get_games_by_game_name('witcher 3', 1, fields='overview'))
