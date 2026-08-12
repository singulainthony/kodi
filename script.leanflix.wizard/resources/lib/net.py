# -*- coding: utf-8 -*-
"""HTTP download helpers (urllib) with Kodi-friendly errors."""

from __future__ import annotations

import os
import re
import ssl
import urllib.error
import urllib.request

import xbmcvfs

from . import kodi
from .constants import DOWNLOAD_TIMEOUT, USER_AGENT


class DownloadError(Exception):
    pass


def _opener():
    try:
        ctx = ssl.create_default_context()
    except Exception:
        ctx = ssl._create_unverified_context()  # noqa: SLF001 — some Kodi Android builds
    return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))


def fetch_bytes(url, timeout=DOWNLOAD_TIMEOUT):
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with _opener().open(request, timeout=timeout) as response:
            status = getattr(response, 'status', None) or response.getcode()
            if status != 200:
                raise DownloadError('HTTP %s for %s' % (status, url))
            data = response.read()
            if not data:
                raise DownloadError('Empty response from %s' % url)
            return data
    except DownloadError:
        raise
    except urllib.error.HTTPError as exc:
        raise DownloadError('HTTP %s for %s' % (exc.code, url)) from exc
    except urllib.error.URLError as exc:
        raise DownloadError('Could not reach %s (%s)' % (url, exc.reason)) from exc
    except Exception as exc:
        raise DownloadError('Download failed for %s: %s' % (url, exc)) from exc


def fetch_text(url, timeout=DOWNLOAD_TIMEOUT):
    data = fetch_bytes(url, timeout=timeout)
    return data.decode('utf-8', errors='replace')


def download_file(url, dest_path, timeout=DOWNLOAD_TIMEOUT):
    data = fetch_bytes(url, timeout=timeout)
    directory = os.path.dirname(dest_path)
    kodi.ensure_dir(directory)
    tmp_path = dest_path + '.part'
    with open(tmp_path, 'wb') as handle:
        handle.write(data)
    if os.path.exists(dest_path):
        try:
            os.remove(dest_path)
        except OSError:
            xbmcvfs.delete(dest_path)
    os.replace(tmp_path, dest_path)
    return dest_path


def find_repo_zip_on_index(index_url):
    """Scrape a directory listing for repository.*.zip links."""
    html = fetch_text(index_url)
    names = re.findall(r'href=["\']([^"\']*repository\.[^"\']+\.zip)["\']', html, re.I)
    if not names:
        names = re.findall(r'(repository\.[A-Za-z0-9._-]+\.zip)', html, re.I)
    if not names:
        return None
    name = names[0]
    if name.startswith('http://') or name.startswith('https://'):
        return name
    base = index_url if index_url.endswith('/') else index_url + '/'
    return urllib.request.urljoin(base, name)
