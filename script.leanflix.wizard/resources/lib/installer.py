# -*- coding: utf-8 -*-
"""Install upstream repos and core add-ons, then switch to Arctic Fuse 3."""

from __future__ import annotations

import os
import re
import zipfile

import xbmc
import xbmcaddon

from . import kodi, net, sources
from .constants import (
    COCOSCRAPERS_ID,
    CORE_INSTALL_TARGETS,
    INSTALL_TIMEOUT_S,
    REDLIGHT_ID,
    REDLIGHT_NAME,
    REPO_WAIT_MS,
    SKIN_ID,
    SKIN_NAME,
    UPSTREAM_REPOS,
    VOD_CANDIDATE_IDS,
    VOD_NAME_HINTS,
)
from .net import DownloadError


def _temp_path(*parts):
    base = kodi.translate_path('special://temp')
    kodi.ensure_dir(base)
    return os.path.join(base, *parts)


def _addons_dir():
    path = kodi.translate_path('special://home/addons')
    kodi.ensure_dir(path)
    return path


def _extract_addon_zip(zip_path, addon_id):
    dest_root = _addons_dir()
    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = zf.namelist()
        if not names:
            raise RuntimeError('Zip is empty: %s' % zip_path)
        top = names[0].split('/')[0]
        if top != addon_id:
            # Still extract; Kodi requires folder name == addon id
            kodi.log('Zip top-level folder %s != %s' % (top, addon_id), xbmc.LOGWARNING)
        zf.extractall(dest_root)
    installed = os.path.join(dest_root, addon_id)
    addon_xml = os.path.join(installed, 'addon.xml')
    if not os.path.isfile(addon_xml):
        raise RuntimeError('Extracted zip did not contain %s/addon.xml' % addon_id)
    return installed


def _enable_and_refresh(addon_id):
    kodi.execute_builtin('UpdateLocalAddons', True)
    kodi.sleep_ms(1000)
    kodi.set_addon_enabled(addon_id, True)
    kodi.sleep_ms(500)


def _candidate_zip_urls(repo):
    urls = list(repo.get('zip_urls') or ())
    try:
        found = net.find_repo_zip_on_index(repo['source_url'])
        if found and found not in urls:
            urls.append(found)
    except DownloadError as exc:
        kodi.log('Could not list %s: %s' % (repo['source_url'], exc), xbmc.LOGWARNING)
    return urls


def install_repository(repo, progress=None, step_label=''):
    addon_id = repo['id']
    if kodi.is_addon_installed(addon_id):
        if not kodi.is_addon_enabled(addon_id):
            kodi.set_addon_enabled(addon_id, True)
        kodi.log('Repository already installed: %s' % addon_id)
        return 'skipped'

    if progress:
        progress.update(progress._percent, step_label, repo['name'], repo['source_url'])

    zip_urls = _candidate_zip_urls(repo)
    if not zip_urls:
        kodi.ok(
            kodi.localized(30000),
            kodi.localized(30040) % (repo['name'], repo['source_url'], 'no zip listed'),
        )
        return 'error'

    last_error = None
    dest = None
    for zip_url in zip_urls:
        filename = os.path.basename(zip_url.split('?')[0]) or ('%s.zip' % addon_id)
        dest = _temp_path(filename)
        try:
            net.download_file(zip_url, dest)
            _extract_addon_zip(dest, addon_id)
            _enable_and_refresh(addon_id)
            last_error = None
            break
        except Exception as exc:
            last_error = exc
            kodi.log('Repo zip failed %s: %s' % (zip_url, exc), xbmc.LOGWARNING)
        finally:
            if dest and os.path.isfile(dest):
                try:
                    os.remove(dest)
                except OSError:
                    pass

    if last_error is not None:
        kodi.ok(
            kodi.localized(30000),
            kodi.localized(30040) % (repo['name'], repo['source_url'], str(last_error)),
        )
        return 'error'

    if not kodi.wait_for_addon(addon_id, timeout_s=30):
        kodi.ok(kodi.localized(30000), kodi.localized(30041) % addon_id)
        return 'error'
    return 'installed'


def _parse_addon_ids_from_xml(xml_text):
    found = []
    for match in re.finditer(r'<addon\b([^>]*)>', xml_text):
        attrs = match.group(1)
        id_m = re.search(r'\bid="([^"]+)"', attrs)
        name_m = re.search(r'\bname="([^"]*)"', attrs)
        if id_m:
            found.append((id_m.group(1), name_m.group(1) if name_m else ''))
    return found


def discover_vod_ids():
    """Prefer IDs advertised by Red Wizard; fall back to Red Light then Fen."""
    discovered = []
    for repo in UPSTREAM_REPOS:
        if repo['id'] != 'repository.redwizard':
            continue
        for xml_url in repo.get('addons_xml') or ():
            try:
                xml_text = net.fetch_text(xml_url)
            except DownloadError as exc:
                kodi.log('Could not fetch %s: %s' % (xml_url, exc), xbmc.LOGWARNING)
                continue
            for addon_id, name in _parse_addon_ids_from_xml(xml_text):
                blob = ('%s %s' % (addon_id, name)).lower()
                hinted = any(hint in blob for hint in VOD_NAME_HINTS)
                if hinted or addon_id in VOD_CANDIDATE_IDS or 'fen' in addon_id.lower():
                    if addon_id not in discovered:
                        discovered.append(addon_id)
                        kodi.log('Discovered VOD candidate %s (%s) from %s' % (addon_id, name, xml_url))
    ordered = []
    for addon_id in list(discovered) + list(VOD_CANDIDATE_IDS):
        if addon_id not in ordered:
            ordered.append(addon_id)
    return ordered


def _install_from_repo(addon_id, label):
    if kodi.is_addon_installed(addon_id):
        if not kodi.is_addon_enabled(addon_id):
            kodi.set_addon_enabled(addon_id, True)
        kodi.log('Already installed: %s' % addon_id)
        return 'skipped'

    kodi.log('InstallAddon(%s) — %s' % (addon_id, label))
    kodi.ok(kodi.localized(30000), kodi.localized(30042) % label)
    kodi.execute_builtin('InstallAddon(%s)' % addon_id, True)
    if kodi.wait_for_addon(addon_id, timeout_s=INSTALL_TIMEOUT_S):
        kodi.set_addon_enabled(addon_id, True)
        return 'installed'
    return 'missing'


def _vod_label(addon_id):
    if addon_id == REDLIGHT_ID:
        return REDLIGHT_NAME
    if 'fen' in addon_id:
        return 'Fen Light AM (%s)' % addon_id
    return addon_id


def install_vod():
    for addon_id in VOD_CANDIDATE_IDS:
        if kodi.is_addon_installed(addon_id):
            if not kodi.is_addon_enabled(addon_id):
                kodi.set_addon_enabled(addon_id, True)
            return addon_id, 'skipped'

    candidates = discover_vod_ids()
    last_status = 'missing'
    for addon_id in candidates:
        status = _install_from_repo(addon_id, _vod_label(addon_id))
        last_status = status
        if status in ('installed', 'skipped'):
            return addon_id, status

    kodi.ok(kodi.localized(30000), kodi.localized(30043) % ', '.join(candidates))
    return None, last_status


def resolve_vod_id():
    for addon_id in VOD_CANDIDATE_IDS:
        if kodi.is_addon_installed(addon_id):
            return addon_id
    return None


def resolve_fen_id():
    """Back-compat alias used by the checklist."""
    return resolve_vod_id()


def switch_skin(prompt=True):
    if not kodi.is_addon_installed(SKIN_ID):
        kodi.ok(kodi.localized(30000), kodi.localized(30044) % SKIN_NAME)
        return False
    if not kodi.is_addon_enabled(SKIN_ID):
        kodi.set_addon_enabled(SKIN_ID, True)
        kodi.sleep_ms(1000)

    try:
        current = xbmcaddon.Addon('skin.estuary')
        del current
    except Exception:
        pass

    if prompt and not kodi.yesno(kodi.localized(30000), kodi.localized(30045) % SKIN_NAME):
        return False

    result = kodi.jsonrpc('Settings.SetSettingValue', {
        'setting': 'lookandfeel.skin',
        'value': SKIN_ID,
    })
    if not kodi.jsonrpc_ok(result):
        kodi.log('Skin switch JSON-RPC failed: %s' % result, xbmc.LOGERROR)
        kodi.ok(kodi.localized(30000), kodi.localized(30046) % SKIN_ID)
        return False
    kodi.notify(kodi.localized(30000), kodi.localized(30047) % SKIN_NAME)
    return True


def install_core_components():
    heading = kodi.localized(30000)
    if not kodi.yesno(heading, kodi.localized(30030)):
        return

    with kodi.Progress(heading) as progress:
        progress.update(5, kodi.localized(30031))
        added, skipped, errors = sources.add_upstream_sources()
        if errors:
            kodi.ok(heading, kodi.localized(30032) % '; '.join(errors))
        kodi.log('Sources added=%s skipped=%s' % (added, skipped))

        if progress.cancelled():
            return

        total_repos = len(UPSTREAM_REPOS)
        for index, repo in enumerate(UPSTREAM_REPOS, start=1):
            percent = 15 + int(35 * index / total_repos)
            progress.update(percent, kodi.localized(30033), repo['name'])
            install_repository(repo, progress=progress, step_label=kodi.localized(30033))
            if progress.cancelled():
                return

        progress.update(55, kodi.localized(30034))
        kodi.execute_builtin('UpdateAddonRepos', True)
        kodi.sleep_ms(REPO_WAIT_MS)

        progress.update(65, kodi.localized(30035) % SKIN_NAME)
        skin_status = _install_from_repo(SKIN_ID, SKIN_NAME)
        if skin_status == 'missing':
            kodi.ok(heading, kodi.localized(30044) % SKIN_NAME)

        if progress.cancelled():
            return

        progress.update(78, kodi.localized(30036))
        fen_id, fen_status = install_vod()

        if progress.cancelled():
            return

        progress.update(88, kodi.localized(30037))
        coco_status = _install_from_repo(COCOSCRAPERS_ID, 'CocoScrapers')
        if coco_status == 'missing':
            kodi.ok(heading, kodi.localized(30048) % COCOSCRAPERS_ID)

        for target in CORE_INSTALL_TARGETS:
            if target['kind'] == 'optional' and not kodi.is_addon_installed(target['id']):
                progress.update(94, kodi.localized(30035) % target['label'])
                _install_from_repo(target['id'], target['label'])

        progress.update(100, kodi.localized(30038))

    summary_lines = [
        kodi.localized(30039),
        'Arctic Fuse 3: %s' % ('ok' if kodi.is_addon_installed(SKIN_ID) else 'missing'),
        'VOD (Red Light / Fen): %s' % (fen_id or 'missing'),
        'CocoScrapers: %s' % ('ok' if kodi.is_addon_installed(COCOSCRAPERS_ID) else 'missing'),
    ]
    kodi.ok(heading, '[CR]'.join(summary_lines))

    if kodi.is_addon_installed(SKIN_ID):
        switch_skin(prompt=True)
        from . import home_preset
        if kodi.yesno(heading, kodi.localized(30079)):
            tv_mode = kodi.yesno(heading, kodi.localized(30080))
            home_preset.apply_netflix_home(prompt=False, tv_mode=tv_mode)

    if fen_id or kodi.is_addon_installed(COCOSCRAPERS_ID):
        from . import checklist
        if kodi.yesno(heading, kodi.localized(30049)):
            checklist.run_checklist()
