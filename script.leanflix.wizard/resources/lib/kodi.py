# -*- coding: utf-8 -*-
"""Thin wrappers around xbmc / xbmcgui / xbmcaddon / xbmcvfs / JSON-RPC."""

from __future__ import annotations

import json
import os
import time

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

from .constants import ADDON_ID

_ADDON = xbmcaddon.Addon(ADDON_ID)


def addon():
    return _ADDON


def localized(string_id, fallback=''):
    text = _ADDON.getLocalizedString(string_id)
    return text if text else fallback


def log(message, level=xbmc.LOGINFO):
    xbmc.log('LeanFlix Wizard: %s' % message, level)


def translate_path(path):
    return xbmcvfs.translatePath(path)


def notify(heading, message, icon=xbmcgui.NOTIFICATION_INFO, ms=4000):
    xbmcgui.Dialog().notification(heading, message, icon, ms)


def ok(heading, message):
    xbmcgui.Dialog().ok(heading, message)


def yesno(heading, message, yeslabel='', nolabel=''):
    kwargs = {}
    if yeslabel:
        kwargs['yeslabel'] = yeslabel
    if nolabel:
        kwargs['nolabel'] = nolabel
    return xbmcgui.Dialog().yesno(heading, message, **kwargs)


def select(heading, options):
    return xbmcgui.Dialog().select(heading, options)


def jsonrpc(method, params=None, rpc_id=1):
    payload = {'jsonrpc': '2.0', 'method': method, 'id': rpc_id}
    if params is not None:
        payload['params'] = params
    raw = xbmc.executeJSONRPC(json.dumps(payload))
    try:
        return json.loads(raw)
    except ValueError:
        log('JSON-RPC parse failure for %s: %s' % (method, raw), xbmc.LOGERROR)
        return {'error': {'message': 'invalid json-rpc response', 'data': raw}}


def jsonrpc_ok(result):
    return isinstance(result, dict) and 'error' not in result


def is_addon_installed(addon_id):
    try:
        xbmcaddon.Addon(addon_id)
        return True
    except RuntimeError:
        pass
    result = jsonrpc('Addons.GetAddonDetails', {
        'addonid': addon_id,
        'properties': ['enabled'],
    })
    return jsonrpc_ok(result) and 'result' in result


def is_addon_enabled(addon_id):
    result = jsonrpc('Addons.GetAddonDetails', {
        'addonid': addon_id,
        'properties': ['enabled'],
    })
    if not jsonrpc_ok(result):
        return False
    try:
        return bool(result['result']['addon']['enabled'])
    except (KeyError, TypeError):
        return False


def set_addon_enabled(addon_id, enabled=True):
    result = jsonrpc('Addons.SetAddonEnabled', {
        'addonid': addon_id,
        'enabled': enabled,
    })
    if not jsonrpc_ok(result):
        log('SetAddonEnabled failed for %s: %s' % (addon_id, result), xbmc.LOGWARNING)
        return False
    return True


def execute_builtin(command, wait=True):
    xbmc.executebuiltin(command, wait)


def sleep_ms(milliseconds):
    xbmc.sleep(int(milliseconds))


def wait_for_addon(addon_id, timeout_s=90, poll_ms=1000):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if is_addon_installed(addon_id):
            return True
        sleep_ms(poll_ms)
        if xbmc.Monitor().abortRequested():
            return False
    return is_addon_installed(addon_id)


def ensure_dir(path):
    if not xbmcvfs.exists(path):
        xbmcvfs.mkdirs(path)
    # xbmcvfs.exists can be flaky on trailing-slash dirs
    if not os.path.isdir(path):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError:
            pass


def copy_file(src, dest):
    if xbmcvfs.exists(dest):
        xbmcvfs.delete(dest)
    return xbmcvfs.copy(src, dest)


def file_exists(path):
    return bool(xbmcvfs.exists(path))


def read_text(path):
    if not xbmcvfs.exists(path):
        return None
    handle = xbmcvfs.File(path, 'r')
    try:
        data = handle.read()
    finally:
        handle.close()
    if isinstance(data, bytes):
        return data.decode('utf-8')
    return data


def write_text(path, text):
    ensure_dir(os.path.dirname(path))
    if xbmcvfs.exists(path):
        xbmcvfs.delete(path)
    payload = text if isinstance(text, str) else text.decode('utf-8')
    handle = xbmcvfs.File(path, 'w')
    try:
        written = handle.write(payload)
    finally:
        handle.close()
    # Kodi versions return True, a byte count, or None on success
    if written is False:
        return False
    if xbmcvfs.exists(path):
        return True
    try:
        return os.path.isfile(path) and os.path.getsize(path) > 0
    except OSError:
        return False


def skin_set_string(name, value):
    execute_builtin('Skin.SetString(%s,%s)' % (name, value), True)


def skin_reset(name):
    execute_builtin('Skin.Reset(%s)' % name, True)


def skin_set_bool(name, enabled=True):
    if enabled:
        execute_builtin('Skin.SetBool(%s)' % name, True)
    else:
        execute_builtin('Skin.Reset(%s)' % name, True)


class Progress(object):
    def __init__(self, heading):
        self._dialog = xbmcgui.DialogProgress()
        self._heading = heading
        self._dialog.create(heading)
        self._percent = 0

    def update(self, percent, line1='', line2='', line3=''):
        self._percent = max(0, min(100, int(percent)))
        message = '[CR]'.join(part for part in (line1, line2, line3) if part)
        try:
            self._dialog.update(self._percent, message)
        except TypeError:
            self._dialog.update(self._percent, line1, line2, line3)

    def cancelled(self):
        return self._dialog.iscanceled()

    def close(self):
        self._dialog.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False
