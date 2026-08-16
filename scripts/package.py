#!/usr/bin/env python3
"""Build LeanFlix addons.xml, checksum, and installable zips."""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ADDONS = (
    ROOT / 'repository.leanflix',
    ROOT / 'script.leanflix.wizard',
)
ZIPS = ROOT / 'zips'
INSTALL = ROOT / 'install'
EXCLUDE_NAMES = {'__pycache__', '.DS_Store', '.git'}
EXCLUDE_SUFFIXES = {'.pyc', '.pyo', '.part'}


def addon_meta(addon_dir: Path) -> tuple[str, str, str]:
    xml_path = addon_dir / 'addon.xml'
    tree = ET.parse(xml_path)
    root = tree.getroot()
    addon_id = root.attrib['id']
    version = root.attrib['version']
    xml_text = xml_path.read_text(encoding='utf-8')
    xml_text = re.sub(r'<\?xml[^?]*\?>\s*', '', xml_text, count=1).strip()
    return addon_id, version, xml_text


def should_skip(path: Path) -> bool:
    if path.name in EXCLUDE_NAMES or path.name.startswith('.'):
        return True
    if path.suffix in EXCLUDE_SUFFIXES:
        return True
    return any(part in EXCLUDE_NAMES for part in path.parts)


def write_zip(addon_dir: Path, addon_id: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(addon_dir.rglob('*')):
            if path.is_dir() or should_skip(path):
                continue
            arcname = Path(addon_id) / path.relative_to(addon_dir)
            zf.write(path, arcname.as_posix())
    print('  wrote', dest.relative_to(ROOT), '(%s bytes)' % dest.stat().st_size)


def build_addons_xml(entries: list[str]) -> bytes:
    body = '\n\n'.join(entries)
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<addons>\n'
        '%s\n'
        '</addons>\n' % body
    )
    return xml.encode('utf-8')


def main() -> int:
    print('Packaging LeanFlix from', ROOT)
    ZIPS.mkdir(parents=True, exist_ok=True)
    INSTALL.mkdir(parents=True, exist_ok=True)

    catalog = []
    zipped = {}
    for addon_dir in ADDONS:
        if not (addon_dir / 'addon.xml').is_file():
            print('missing addon.xml in', addon_dir, file=sys.stderr)
            return 1
        addon_id, version, xml_text = addon_meta(addon_dir)
        zip_name = '%s-%s.zip' % (addon_id, version)
        dest = ZIPS / addon_id / zip_name
        write_zip(addon_dir, addon_id, dest)
        zipped[addon_id] = dest
        # Drop leftover versioned zips (e.g. wizard 1.0.1 next to 1.0.2)
        for old in (ZIPS / addon_id).glob('%s-*.zip' % addon_id):
            if old.name != zip_name:
                old.unlink()
                print('  removed leftover', old.relative_to(ROOT))
        for old in INSTALL.glob('%s-*.zip' % addon_id):
            if old.name != zip_name:
                old.unlink()
                print('  removed leftover', old.relative_to(ROOT))
        # Repo catalog lists only the wizard (repo is installed from zip first).
        if addon_id != 'repository.leanflix':
            catalog.append(xml_text)

    xml_bytes = build_addons_xml(catalog)
    (ZIPS / 'addons.xml').write_bytes(xml_bytes)
    md5 = hashlib.md5(xml_bytes).hexdigest() + '\n'
    (ZIPS / 'addons.xml.md5').write_text(md5, encoding='ascii')
    print('  wrote zips/addons.xml (%s bytes)' % len(xml_bytes))
    print('  wrote zips/addons.xml.md5', md5.strip())

    repo_zip = zipped['repository.leanflix']
    wizard_zip = zipped['script.leanflix.wizard']
    shutil.copy2(repo_zip, INSTALL / repo_zip.name)
    shutil.copy2(wizard_zip, INSTALL / wizard_zip.name)
    shutil.copy2(repo_zip, ROOT / repo_zip.name)
    pages = ROOT / 'repo'
    pages.mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo_zip, pages / repo_zip.name)
    shutil.copy2(wizard_zip, pages / wizard_zip.name)
    for old in pages.glob('script.leanflix.wizard-*.zip'):
        if old.name != wizard_zip.name:
            old.unlink()
            print('  removed leftover', old.relative_to(ROOT))
    print('  copied convenience zips to install/, repo/, and repository.leanflix-*.zip at repo root')
    print('Done.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
