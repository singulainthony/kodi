# -*- coding: utf-8 -*-
"""Post-install checklist: Real-Debrid, Trakt, CocoScrapers, widgets."""

from __future__ import annotations

import xbmcaddon

from . import home_preset, installer, kodi
from .constants import (
    COCOSCRAPERS_ID,
    FEN_EXTERNAL_ENABLE_KEYS,
    FEN_EXTERNAL_MODULE_KEYS,
    RD_DEVICE_URL,
    SKIN_ID,
    TMDBHELPER_ID,
    TRAKT_URL,
)


def open_fen_settings(fen_id=None):
    fen_id = fen_id or installer.resolve_fen_id()
    if not fen_id:
        kodi.ok(kodi.localized(30000), kodi.localized(30050))
        return False
    kodi.execute_builtin('Addon.OpenSettings(%s)' % fen_id, True)
    return True


def open_fen_addon(fen_id=None):
    fen_id = fen_id or installer.resolve_fen_id()
    if not fen_id:
        kodi.ok(kodi.localized(30000), kodi.localized(30050))
        return False
    kodi.execute_builtin('RunAddon(%s)' % fen_id, True)
    return True


def _try_enable_cocoscrapers(fen_id):
    if not kodi.is_addon_installed(COCOSCRAPERS_ID):
        return False
    try:
        fen = xbmcaddon.Addon(fen_id)
    except RuntimeError:
        return False
    enabled = False
    for key in FEN_EXTERNAL_ENABLE_KEYS:
        try:
            fen.setSetting(key, 'true')
            enabled = True
        except Exception:
            continue
    for key in FEN_EXTERNAL_MODULE_KEYS:
        try:
            fen.setSetting(key, COCOSCRAPERS_ID)
            enabled = True
        except Exception:
            continue
    return enabled


def _authorize_real_debrid():
    fen_id = installer.resolve_fen_id()
    kodi.ok(kodi.localized(30060), kodi.localized(30061) % RD_DEVICE_URL)
    if fen_id:
        open_fen_settings(fen_id)


def _authorize_trakt():
    fen_id = installer.resolve_fen_id()
    kodi.ok(kodi.localized(30062), kodi.localized(30063) % TRAKT_URL)
    if fen_id:
        open_fen_settings(fen_id)


def _enable_coco_in_fen():
    fen_id = installer.resolve_fen_id()
    if not fen_id:
        kodi.ok(kodi.localized(30000), kodi.localized(30050))
        return
    attempted = _try_enable_cocoscrapers(fen_id)
    extra = kodi.localized(30065) if attempted else ''
    kodi.ok(kodi.localized(30064), kodi.localized(30066) % extra)
    open_fen_settings(fen_id)


def _widget_tips():
    skin_ok = 'yes' if kodi.is_addon_installed(SKIN_ID) else 'no'
    tmdb_ok = 'yes' if kodi.is_addon_installed(TMDBHELPER_ID) else 'no'
    kodi.ok(
        kodi.localized(30067),
        kodi.localized(30068) % (skin_ok, tmdb_ok),
    )


def run_checklist():
    heading = kodi.localized(30011)
    items = [
        kodi.localized(30060),  # Authorize Real-Debrid
        kodi.localized(30062),  # Authorize Trakt (VOD)
        kodi.localized(30074),  # Authorize Trakt in TMDb Helper
        kodi.localized(30070),  # Apply Netflix home widgets
        kodi.localized(30083),  # Optimize for TV / slow device
        kodi.localized(30064),  # Enable CocoScrapers in Fen
        kodi.localized(30067),  # Widget tips
        kodi.localized(30012),  # Open Fen settings
        kodi.localized(30069),  # Done
    ]
    while True:
        choice = kodi.select(heading, items)
        if choice == 0:
            _authorize_real_debrid()
        elif choice == 1:
            _authorize_trakt()
        elif choice == 2:
            home_preset.open_tmdbhelper_trakt()
        elif choice == 3:
            home_preset.apply_netflix_home(prompt=True)
        elif choice == 4:
            home_preset.apply_tv_performance(prompt=True)
        elif choice == 5:
            _enable_coco_in_fen()
        elif choice == 6:
            _widget_tips()
        elif choice == 7:
            open_fen_settings()
        else:
            break
