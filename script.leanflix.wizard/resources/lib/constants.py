# -*- coding: utf-8 -*-
"""Verified and well-known IDs / URLs for the LeanFlix stack (Kodi 21)."""

ADDON_ID = 'script.leanflix.wizard'
WIZARD_VERSION = '1.0.3'
USER_AGENT = 'Kodi/21.0 (LeanFlixWizard/%s)' % WIZARD_VERSION

# Skin (verified 2026-08 from jurialmunkey omega addons.xml)
SKIN_ID = 'skin.arctic.fuse.3'
SKIN_NAME = 'Arctic Fuse 3'
TMDBHELPER_ID = 'plugin.video.themoviedb.helper'
SKINVARIABLES_ID = 'script.skinvariables'

# Primary VOD — Red Light is currently listed in The Red Repo (verified 2026-08).
# Fen Light AM was removed from that catalog; keep Fen IDs as fallbacks.
REDLIGHT_ID = 'plugin.video.redlight'
REDLIGHT_NAME = 'Red Light'
FEN_CANDIDATE_IDS = (
    'plugin.video.fenlightam',
    'plugin.video.fenlight',
)
VOD_CANDIDATE_IDS = (REDLIGHT_ID,) + FEN_CANDIDATE_IDS
FEN_NAME_HINTS = ('fen light', 'fenlight', 'fenlightam', 'fen light am')
VOD_NAME_HINTS = FEN_NAME_HINTS + ('red light', 'redlight')

# CocoScrapers (verified 2026-08 from not-coco-joe addons.xml)
COCOSCRAPERS_ID = 'script.module.cocoscrapers'

# File-manager sources + repository zips (verified live 2026-08)
UPSTREAM_REPOS = (
    {
        'id': 'repository.jurialmunkey',
        'name': 'jurialmunkey',
        'source_name': 'jurialmunkey',
        'source_url': 'https://jurialmunkey.github.io/repository.jurialmunkey/',
        'zip_urls': (
            'https://jurialmunkey.github.io/repository.jurialmunkey/repository.jurialmunkey-3.4.zip',
        ),
        'addons_xml': (
            'https://raw.githubusercontent.com/jurialmunkey/repository.jurialmunkey/master/omega/zips/addons.xml',
        ),
    },
    {
        'id': 'repository.redwizard',
        'name': 'The Red Repo',
        'source_name': 'redwizard',
        'source_url': 'https://repo.redwizard.xyz',
        'zip_urls': (
            'https://repo.redwizard.xyz/repository.redwizard-1.2.2.zip',
        ),
        'addons_xml': (
            'https://repo.redwizard.xyz/redwizardrepo/main/addons.xml',
            'https://repo.redwizard.xyz/redwizardrepo/21omega/addons.xml',
        ),
    },
    {
        'id': 'repository.cocoscrapers',
        'name': 'CocoScrapers Repository',
        'source_name': 'cocojoe',
        'source_url': 'https://cocojoe2411.github.io/',
        'zip_urls': (
            'https://cocojoe2411.github.io/repository.cocoscrapers-1.0.1.zip',
        ),
        'addons_xml': (
            'https://raw.githubusercontent.com/not-coco-joe/repository.cocoscrapers/master/zips/addons.xml',
            'https://raw.githubusercontent.com/CocoJoe2411/repository.cocoscrapers/master/zips/addons.xml',
        ),
    },
)

CORE_INSTALL_TARGETS = (
    {'id': SKIN_ID, 'label': SKIN_NAME, 'kind': 'skin'},
    {'id': COCOSCRAPERS_ID, 'label': 'CocoScrapers Module', 'kind': 'module'},
    {'id': TMDBHELPER_ID, 'label': 'TMDb Helper', 'kind': 'optional'},
)

RD_DEVICE_URL = 'https://real-debrid.com/device'
TRAKT_URL = 'https://trakt.tv'

# Fen Light setting keys tried when enabling CocoScrapers (forks differ)
FEN_EXTERNAL_ENABLE_KEYS = (
    'external_scrapers',
    'provider.external',
    'external.provider',
    'enable_external_scrapers',
    'module.provider',
)
FEN_EXTERNAL_MODULE_KEYS = (
    'external_scraper.module',
    'external_scrapers.module',
    'module.provider',
    'external.provider.module',
    'scraper_package',
)

DOWNLOAD_TIMEOUT = 45
REPO_WAIT_MS = 2500
INSTALL_POLL_MS = 1000
INSTALL_TIMEOUT_S = 90
