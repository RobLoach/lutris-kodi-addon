"""Runner for stella Atari 2600 emulator"""
import os
from lutris import settings
from lutris.runners.runner import Runner


class stella(Runner):
    description = "Atari 2600 emulator"
    human_name = "Stella"
    platform = "Atari 2600"
    runnable_alone = True
    game_options = [
        {
            "option": "main_file",
            "type": "file",
            "label": "ROM file",
            'help': ("The game data, commonly called a ROM image.\n"
                     "Supported formats: A26/BIN/ROM. GZIP and ZIP compressed "
                     "ROMs are supported.")
        }
    ]
    runner_options = []

    def get_executable(self):
        return os.path.join(settings.RUNNER_DIR, "stella/bin/stella")

    def play(self):
        cart = self.game_config.get('main_file') or ''
        if not os.path.exists(cart):
            return {'error': 'FILE_NOT_FOUND', 'file': cart}
        return {'command': [self.get_executable(), cart]}
