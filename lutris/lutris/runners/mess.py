import os
from lutris import settings
from lutris.runners.runner import Runner


class mess(Runner):
    human_name = "MESS"
    description = "Multi-system (consoles and computers) emulator"
    platform = 'multi-platform'
    game_options = [
        {
            'option': 'main_file',
            'type': 'file',
            'label': 'ROM file',
            'help': ("The game data, commonly called a ROM image.")
        },
        {
            'option': 'machine',
            'type': 'choice_with_entry',
            'label': "Machine",
            'choices': [
                ("Amstrad CPC 464", 'cpc464'),
                ("Amstrad CPC 6128", 'cpc6128'),
                ("Amstrad GX4000", 'gx4000'),
                ("Apple II", 'apple2'),
                ("Commodore 64", 'c64'),
                ("ZX Spectrum", 'spectrum'),
                ("ZX Spectrum 128", 'spec128'),
            ],
            'help': ("The emulated machine.")
        },
        {
            'option': 'device',
            'type': 'choice_with_entry',
            'label': "Storage type",
            'choices': [
                ("Floppy disk", 'flop'),
                ("Floppy drive 1", 'flop1'),
                ("Floppy drive 2", 'flop2'),
                ("Cassette (tape)", 'cass'),
                ("Cartridge", 'cart'),
                ("Snapshot", 'snapshot'),
                ("Quickload", 'quickload'),
                ("CDROM", 'cdrm'),
            ]
        }
    ]
    runner_options = [
        {
            'option': 'rompath',
            'type': 'directory_chooser',
            'label': "BIOS path",
            'help': ("Choose the folder containing MESS bios files.\n"
                     "These files contain code from the original hardware "
                     "necessary to the emulation.")
        }
    ]

    def get_executable(self):
        return os.path.join(settings.RUNNER_DIR, "mess/mess")

    @property
    def working_dir(self):
        return os.path.join(os.path.expanduser("~"), ".mame")

    def play(self):
        rompath = self.runner_config.get('rompath') or ''
        if not os.path.exists(rompath):
            rompath = os.path.join(settings.RUNNER_DIR, "mess/bios")
        if not os.path.exists(rompath):
            return {'error': 'NO_BIOS'}
        machine = self.game_config.get('machine')
        if not machine:
            return {'error': 'INCOMPLETE_CONFIG'}
        rom = self.game_config.get('main_file') or ''
        if rom and not os.path.exists(rom):
            return {'error': 'FILE_NOT_FOUND', 'file': rom}
        device = self.game_config.get('device')
        command = [self.get_executable(),
                   '-uimodekey', 'RCONTROL',
                   '-rompath', rompath, machine]
        if device:
            command.append('-' + device)
        if rom:
            command.append(rom)
        return {'command': command}
