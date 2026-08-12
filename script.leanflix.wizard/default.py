# -*- coding: utf-8 -*-
"""LeanFlix Wizard entry point (Kodi 21 Omega)."""

from __future__ import annotations

import sys

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

_ADDON_PATH = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('path'))
if _ADDON_PATH not in sys.path:
    sys.path.insert(0, _ADDON_PATH)

from resources.lib import checklist, home_preset, installer  # noqa: E402
from resources.lib.kodi import localized, notify, yesno  # noqa: E402


def _main_menu():
    options = [
        localized(30010),  # Install core components
        localized(30011),  # Setup checklist
        localized(30070),  # Apply Netflix home widgets
        localized(30012),  # Open VOD add-on settings
        localized(30013),  # Switch skin to Arctic Fuse 3
        localized(30014),  # Exit
    ]
    return xbmcgui.Dialog().select(localized(30000), options)


def main():
    xbmc.log('LeanFlix Wizard: starting', xbmc.LOGINFO)
    if yesno(localized(30000), localized(30020)):
        installer.install_core_components()

    while True:
        choice = _main_menu()
        if choice == 0:
            installer.install_core_components()
        elif choice == 1:
            checklist.run_checklist()
        elif choice == 2:
            home_preset.apply_netflix_home(prompt=True)
        elif choice == 3:
            checklist.open_fen_settings()
        elif choice == 4:
            installer.switch_skin()
        else:
            notify(localized(30000), localized(30021))
            break


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        xbmc.log('LeanFlix Wizard crashed: %s' % exc, xbmc.LOGERROR)
        xbmcgui.Dialog().ok(
            localized(30000),
            localized(30022) % str(exc),
        )
        sys.exit(1)
