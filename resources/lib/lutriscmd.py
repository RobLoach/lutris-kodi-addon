import os
from distutils.spawn import find_executable
from subprocess import check_output

import simplejson
import xbmc


# Usage:
#   lutris [OPTION…] URI
#
# Run a game directly by adding the parameter lutris:rungame/game-identifier.
# If several games share the same identifier you can use the numerical ID (displayed when running lutris --list-games) and add lutris:rungameid/numerical-id.
# To install a game, add lutris:install/game-identifier.
#
# Help Options:
#   -h, --help                 Show help options
#   --help-all                 Show all help options
#   --help-gapplication        Show GApplication options
#   --help-gtk                 Show GTK+ Options
#
# Application Options:
#   -v, --version              Print the version of Lutris and exit
#   -d, --debug                Show debug messages
#   -i, --install              Install a game from a yml file
#   -e, --exec                 Execute a program with the lutris runtime
#   -l, --list-games           List all games in database
#   -o, --installed            Only list installed games
#   -s, --list-steam-games     List available Steam games
#   --list-steam-folders       List all known Steam library folders
#   -j, --json                 Display the list of games in JSON format
#   --reinstall                Reinstall game
#   --submit-issue             Submit an issue
#   --display=DISPLAY          X display to use

class LutrisCMD(object):
    def __init__(self, bin=None):
        if bin is not None:
            self.bin = bin
        else:
            # Find the path to the lutris executable
            self.bin = find_executable("lutris")
            # Print the excecutable path to the log
            xbmc.log(self.bin, level=xbmc.LOGDEBUG)

    def installGame(self):
        pass

    def playGame(self, gameid=None):
        if gameid is None:
            cmd = self.bin
        else:
            cmd = self.bin + ' lutris:rungameid/' + gameid

        # Log lutris command to kodi.log
        xbmc.log(cmd, level=xbmc.LOGDEBUG)

        # Stop playback if Kodi is playing any media
        if xbmc.Player().isPlaying():
            xbmc.Player().stop()

        # Get Users shutdowntimer value and save it so we can reset it to users value after the game has been quitted
        dpmssetting = simplejson.loads(xbmc.executeJSONRPC(
            '{ "jsonrpc": "2.0", "id": 0, "method": "Settings.getSettingValue", "params" : {"setting": "powermanagement.shutdowntime"} }'))

        # Disable Shutdowntimer (Set Value to 0)

        xbmcsetting = xbmc.executeJSONRPC('{ '
                                          '"jsonrpc": "2.0", '
                                          '"id": 0, '
                                          '"method": "Settings.SetSettingValue", '
                                          '"params" : {"setting": "powermanagement.shutdowntime", '
                                          '"value": 0} }')

        # Launch Lutris
        os.system(cmd)

        # Reset shutdowntimer to users value
        xbmcsetting = xbmc.executeJSONRPC('{ '
                                          '"jsonrpc": "2.0", '
                                          '"id": 0, '
                                          '"method": "Settings.SetSettingValue", '
                                          '"params" : {"setting": "powermanagement.shutdowntime", '
                                          '"value": ' + str(dpmssetting['result']['value']) + '} }')

    def listGames(self, installed=False, json=False):
        """
        Get a list of installed games from lutris as a JSON object and convert it to a Python array.

        note:: JSON object returned from Lutris looks as follows:
        [
          {
            "id": 74,
            "slug": "a-story-about-my-uncle",
            "name": "A Story About My Uncle",
            "runner": "steam",
            "directory": ""
          },
          {
            ...
          }
        ]

        :param installed: If True only installed games will be returned
        :param json:  If True returns as Json else as Python dictonary
        :return:
        """

        cmd = self.bin + ' --list-games --json'
        if installed:
            cmd += ' --installed'

        try:
            result = check_output(cmd, shell=True)
        except Exception as e:
            # Log error if list could not be found
            xbmc.log(e, level=xbmc.LOGERROR)
            result = '{}'

        if json:
            games = result
        else:
            # Parse the list of games from JSON to a Python dictonary.
            games = simplejson.loads(result)

        return games
