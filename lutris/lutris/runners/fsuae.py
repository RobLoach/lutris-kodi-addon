import os

from lutris import settings
from lutris.runners.runner import Runner
from lutris.util.display import get_current_resolution


class fsuae(Runner):
    human_name = "FS-UAE"
    description = "Amiga emulator"
    platform = "Amiga"
    game_options = [
        {
            'option': "main_file",
            'type': "file",
            'label': "Boot disk",
            'default_path': 'game_path',
            'help': ("The main floppy disk file with the game data. \n"
                     "FS-UAE supports floppy images in multiple file formats: "
                     "ADF, IPF, DMS are the most common. ADZ (compressed ADF) "
                     "and ADFs in zip files are a also supported.")
        },
        {
            "option": "disks",
            "type": "multiple",
            "label": "Additionnal floppies",
            'default_path': 'game_path',
            'help': ("The additional floppy disk image(s).")
        }
    ]

    runner_options = [
        {
            "option": "model",
            "label": "Amiga model",
            "type": "choice",
            "choices": [
                ("Amiga 500", 'A500'),
                ("Amiga 500+ with 1 MB chip RAM", 'A500+'),
                ("Amiga 600 with 1 MB chip RAM", 'A600'),
                ("Amiga 1000 with 512 KB chip RAM", 'A1000'),
                ("Amiga 1200 with 2 MB chip RAM", 'A1200'),
                ("Amiga 1200 but with 68020 processor", 'A1200/020'),
                ("Amiga 4000 with 2 MB chip RAM and a 68040", 'A4000/040'),
                ("CD32 unit", 'CD32'),
                ("Commodore CDTV unit", 'CDTV'),
            ],
            'default': 'A500',
            'help': ("Specify the Amiga model you want to emulate.")
        },
        {
            "option": "kickstart_file",
            "label": "Kickstart ROMs location",
            "type": "file",
            'help': ("Choose the folder containing original Amiga kickstart "
                     "ROMs. Refer to FS-UAE documentation to find how to "
                     "acquire them. Without these, FS-UAE uses a bundled "
                     "replacement ROM which is less compatible with Amiga "
                     "software.")
        },
        {
            'option': 'kickstart_ext_file',
            'label': 'Extended Kickstart location',
            'type': 'file',
            'help': 'Location of extended Kickstart used for CD32'
        },
        {
            "option": "gfx_fullscreen_amiga",
            "label": "Fullscreen (F12 + s to switch)",
            "type": "bool",
            'default': False,
        },
        {
            "option": "scanlines",
            "label": "Scanlines display style",
            "type": "bool",
            'default': False,
            'help': ("Activates a display filter adding scanlines to imitate "
                     "the displays of yesteryear.")
        }
    ]

    def insert_floppies(self):
        disks = []
        main_disk = self.game_config.get('main_file')
        if main_disk:
            disks.append(main_disk)

        game_disks = self.game_config.get('disks') or []
        for disk in game_disks:
            if disk not in disks:
                disks.append(disk)
        amiga_model = self.runner_config.get('model')
        if amiga_model in ('CD32', 'CDTV'):
            disk_param = 'cdrom_drive'
        else:
            disk_param = 'floppy_drive'
        floppy_drives = []
        floppy_images = []
        for drive, disk in enumerate(disks):
            floppy_drives.append("--%s_%d=%s" % (disk_param, drive, disk))
            floppy_images.append("--floppy_image_%d=%s" % (drive, disk))
        return floppy_drives + floppy_images

    def get_executable(self):
        return os.path.join(settings.RUNNER_DIR, 'fs-uae/fs-uae')

    def get_params(self):
        params = []
        model = self.runner_config.get('model')
        kickstart_file = self.runner_config.get('kickstart_file')
        if kickstart_file:
            params.append("--kickstart_file=%s" % kickstart_file)
        kickstart_ext_file = self.runner_config.get('kickstart_ext_file')
        if kickstart_ext_file:
            params.append('--kickstart_ext_file=%s' % kickstart_ext_file)
        if model:
            params.append('--amiga_model=%s' % model)
        if self.runner_config.get('gfx_fullscreen_amiga'):
            width = int(get_current_resolution().split('x')[0])
            params.append("--fullscreen")
            # params.append("--fullscreen_mode=fullscreen-window")
            params.append("--fullscreen_mode=fullscreen")
            params.append("--fullscreen_width=%d" % width)
        if self.runner_config.get('scanlines'):
            params.append("--scanlines=1")
        return params

    def play(self):
        params = self.get_params()
        disks = self.insert_floppies()
        command = [self.get_executable()]
        for param in params:
            command.append(param)
        for disk in disks:
            command.append(disk)
        return {'command': command}
