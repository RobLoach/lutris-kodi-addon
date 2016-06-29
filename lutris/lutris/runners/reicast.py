# -*- coding: utf-8 -*-
import os
from lutris import settings
from lutris.runners.runner import Runner


class reicast(Runner):
    human_name = "Reicast"
    description = "Sega Dreamcast emulator"
    platform = "Sega Dreamcast"

    game_options = [{
        'option': 'iso',
        'type': 'file',
        'label': 'Disc image file',
        'help': ("The game data.\n"
                 "Supported formats: ISO, CDI")
    }]

    runner_options = [
        {
            "option": "fullscreen",
            "type": "bool",
            "label": "Fullscreen",
            'default': False,
        }
    ]

    def get_executable(self):
        return os.path.join(settings.RUNNER_DIR, 'reicast/reicast.elf')

    def play(self):
        iso = self.game_config.get('iso')
        fullscreen = '1' if self.runner_config.get('fullscreen') else '0'
        command = [
            self.get_executable(),
            "-config", "config:image={}".format(iso),
            "-config", "x11:fullscreen={}".format(fullscreen)
        ]
        return {'command': command}
