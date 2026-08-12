# -*- coding: utf-8 -*-
"""Add Kodi File Manager sources for upstream repositories."""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET

import xbmc

from . import kodi
from .constants import UPSTREAM_REPOS


SOURCES_PATH = 'special://userdata/sources.xml'
MEDIA_SECTIONS = ('programs', 'video', 'music', 'pictures', 'files')


def _blank_sources_tree():
    root = ET.Element('sources')
    for section in MEDIA_SECTIONS:
        node = ET.SubElement(root, section)
        default = ET.SubElement(node, 'default')
        default.set('pathversion', '1')
        default.text = ''
    return ET.ElementTree(root)


def _load_sources_tree(path):
    if not os.path.isfile(path):
        return _blank_sources_tree()
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        if root is None or root.tag != 'sources':
            kodi.log('sources.xml root is not <sources>; recreating', xbmc.LOGWARNING)
            return _blank_sources_tree()
        for section in MEDIA_SECTIONS:
            if root.find(section) is None:
                node = ET.SubElement(root, section)
                default = ET.SubElement(node, 'default')
                default.set('pathversion', '1')
                default.text = ''
        return tree
    except ET.ParseError as exc:
        kodi.log('Could not parse sources.xml (%s); recreating' % exc, xbmc.LOGWARNING)
        return _blank_sources_tree()


def _source_exists(files_node, name, url):
    for source in files_node.findall('source'):
        existing_name = (source.findtext('name') or '').strip()
        existing_path = (source.findtext('path') or '').strip().rstrip('/')
        if existing_name.lower() == name.lower():
            return True
        if existing_path.rstrip('/') == url.rstrip('/'):
            return True
    return False


def _add_source_xml(name, url):
    path = kodi.translate_path(SOURCES_PATH)
    kodi.ensure_dir(os.path.dirname(path))
    tree = _load_sources_tree(path)
    root = tree.getroot()
    files_node = root.find('files')
    if files_node is None:
        files_node = ET.SubElement(root, 'files')
        default = ET.SubElement(files_node, 'default')
        default.set('pathversion', '1')
        default.text = ''
    if _source_exists(files_node, name, url):
        kodi.log('File source already present: %s' % name)
        return False
    source = ET.SubElement(files_node, 'source')
    ET.SubElement(source, 'name').text = name
    path_el = ET.SubElement(source, 'path')
    path_el.set('pathversion', '1')
    path_el.text = url if url.endswith('/') else url + '/'
    ET.SubElement(source, 'allowsharing').text = 'true'
    tree.write(path, encoding='utf-8', xml_declaration=True)
    kodi.log('Added file source %s -> %s' % (name, url))
    return True


def _add_source_jsonrpc(name, url):
    directory = url if url.endswith('/') else url + '/'
    # Kodi versions differ on param names; try the documented shape first.
    attempts = (
        {'media': 'files', 'name': name, 'directory': directory},
        {'media': 'files', 'source': {'name': name, 'path': directory}},
    )
    for params in attempts:
        result = kodi.jsonrpc('Files.AddSource', params)
        if kodi.jsonrpc_ok(result):
            kodi.log('Files.AddSource succeeded for %s' % name)
            return True
        kodi.log('Files.AddSource attempt failed: %s' % result, xbmc.LOGDEBUG)
    return False


def add_file_source(name, url):
    added_rpc = _add_source_jsonrpc(name, url)
    added_xml = _add_source_xml(name, url)
    return added_rpc or added_xml


def add_upstream_sources():
    added = []
    skipped = []
    errors = []
    for repo in UPSTREAM_REPOS:
        try:
            if add_file_source(repo['source_name'], repo['source_url']):
                added.append(repo['source_name'])
            else:
                skipped.append(repo['source_name'])
        except Exception as exc:
            kodi.log('Failed adding source %s: %s' % (repo['source_name'], exc), xbmc.LOGERROR)
            errors.append('%s: %s' % (repo['source_name'], exc))
    return added, skipped, errors
