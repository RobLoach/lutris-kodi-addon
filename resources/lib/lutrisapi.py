import requests
import xbmc


# TODO: perform full functionality test

class LutrisAPI(object):
    def __init__(self, username=None, password=None):
        """
        Create a Lutris.net Client API Object
        :param username: Lutris.net Username
        :param password: Lutris.net Password
        """
        self.username = username
        self.password = password
        self.token = None
        self.api = 'https://lutris.net/api'

    def genToken(self):
        """
        Generate Token for user specific API calls
        :return: Nothing
        """
        if self.username is None or self.password is None:
            return

        url = self.api + '/accounts/token'

        headers = {
            'Content-Type: application/json',
        }

        data = '{"username": {username},' \
               '"password": {password} }'.format(username=self.username, password=self.password)

        try:
            response = requests.post(url, headers=headers, data=data)
        except requests.exceptions.HTTPError as err:
            xbmc.log('Request Error Lutris API: {0}'.format(err), xbmc.LOGWARNING)
            return err

        data = response.json()
        self.token = data["token"]
        return self.token

    def getGames(self):
        """
        Get all games from Lutris.net
        :return: Returns the game list from Lutris.net
        """
        url = self.api + '/games'

        try:
            response = requests.get(url)
        except requests.exceptions.HTTPError as err:
            xbmc.log('Request Error Lutris API: {0}'.format(err), xbmc.LOGWARNING)
            return err

        data = response.json()
        return data

    def getGameBySlug(self, slug):
        """
        Get game information from Lutris.net providing the game slug
        :param slug: Lutris.net game slug
        :return: dictonary with game information
        """
        url = self.api + '/games/{slug}'.format(slug=slug)

        try:
            response = requests.get(url)
        except requests.exceptions.HTTPError as err:
            xbmc.log('Request Error Lutris API: {0}'.format(err), xbmc.LOGWARNING)
            return err

        response.encoding = 'utf-8'
        data = response.json()
        return data

    def getRunners(self):
        """
        Get all Runners from Lutris.net
        :return: Returns the runners list from Lutris.net
        """
        url = self.api + '/runners'

        try:
            response = requests.get(url)
        except requests.exceptions.HTTPError as err:
            xbmc.log('Request Error Lutris API: {0}'.format(err), xbmc.LOGWARNING)
            return err

        data = response.json()
        return data

    def getLibrary(self):
        """
        Get user specific games library
        :return: Returns a user library from Lutris.net
        """
        if self.username is None or self.password is None:
            return

        if self.token is None:
            self.genToken()

        url = self.api + '/games/library/{username}'.format(username=self.username)

        headers = {
            'Authorization: Token {token}'.format(token=self.token),
        }

        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.HTTPError as err:
            xbmc.log('Request Error Lutris API: {0}'.format(err), xbmc.LOGWARNING)
            return err

        data = response.json()
        return data

    def getIcon(self, icon_url):
        """
        Get the .png icon from the Lutris Server
        :param icon_url: Lutris.net icon url
        :return: File Object
        """
        url = self.api + icon_url

        try:
            response = requests.get(url)
        except requests.exceptions.HTTPError as err:
            xbmc.log('Request Error Lutris API: {0}'.format(err), xbmc.LOGWARNING)
            return err

        return response

    def getBanner(self, banner_url):
        """
        Get the .jpg banner from the Lutris Server
        :param banner_url:
        :return: File Object
        """

        return self.getIcon(banner_url)
