# Lutris Kodi Addon

[Kodi](http://kodi.tv) addon to launch games through [Lutris](http://lutris.net).

![Lutris Kodi Addon Screenshot](resources/media/screenshot.jpg "Lutris Kodi Addon")

## Install

There are a few different ways to install the Lutris Kodi addon...

### [SuperRepo](https://superrepo.org)

1. [Install and setup Lutris](https://lutris.net/downloads/)

1. [Install the SuperRepo repository](https://superrepo.org/get-started/)

1. Visit Home -> Settings -> Addons -> Install from repository -> SuperRepo -> Program Add-ons -> Lutris -> Install

1. Configure the addon to ensure the Lutris executable path is correct

### Manually

1. [Install and setup Lutris](https://lutris.net/downloads/)

1. Enter the command line interface and run the following commands:

    ```
    wget -O lutris-kodi-addon-master.zip https://github.com/RobLoach/script.lutris/archive/master.zip
    unzip lutris-kodi-addon-master.zip
    mkdir ~/.kodi/addons/script.lutris
    cp -r lutris-kodi-addon-master/* .kodi/addons/script.lutris/
    ```

## Development

```bash
git clone git@github.com:RobLoach/script.lutris.git ~/.kodi/addons/script.lutris
cd ~/.kodi/addons/script.lutris
git status
```

## About

- Author: [Rob Loach](http://robloach.net)
- Source: [GitHub](http://github.com/RobLoach/script.lutris/)
