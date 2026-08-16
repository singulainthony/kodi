# -*- coding: utf-8 -*-
"""Apply Netflix-style Arctic Fuse 3 home widgets via skinvariables JSON.

Fuse 3 default home rows are local-library smart playlists
(special://skin/extras/playlists/*.xsp). LeanFlix has no video library, so those
rows stay empty even when Red Light search works. This preset points widgets at
TMDb Helper plugin:// lists (verified 2026 against plugin.video.themoviedb.helper
ROUTE_NOID + jurialmunkey.parser.reconfigure_legacy_params).
"""

from __future__ import annotations

import json
import os
import time

import xbmc
import xbmcaddon

from . import installer, kodi
from .constants import (
    FEN_CANDIDATE_IDS,
    REDLIGHT_ID,
    SKIN_ID,
    SKINVARIABLES_ID,
    TMDBHELPER_ID,
)

TMDBH = 'plugin://plugin.video.themoviedb.helper/'
WIDGET_FLAGS = 'nextpage=false&widget=true'
# Sony / built-in smart TVs choke on 20+ high-res posters at once
TV_WIDGET_LIMIT = 10

# userdata/addon_data/script.skinvariables/nodes/skin.arctic.fuse.3/
NODES_SUBDIR = os.path.join('script.skinvariables', 'nodes', SKIN_ID)
PLAYERS_SUBDIR = os.path.join(TMDBHELPER_ID, 'players')

# Fuse 3 hub switcher (1080i/Includes_Home.xml, skinvariables-startup.json)
LIVE_TV_TOGGLE = 'HomeSwitcher.1107.Toggle'


def _tmdb(info, tmdb_type, limit=None):
    url = '%s?info=%s&tmdb_type=%s&%s' % (TMDBH, info, tmdb_type, WIDGET_FLAGS)
    if limit:
        url += '&limit=%s' % int(limit)
    return url


def _item(label, path, guid, icon=''):
    return {
        'label': label,
        'icon': icon,
        'path': path,
        'target': 'videos',
        'guid': guid,
    }


def home_widgets(tv_mode=False):
    """Home hub: TMDb rows first so the wall is never blank pre-Trakt."""
    limit = TV_WIDGET_LIMIT if tv_mode else None
    if tv_mode:
        return [
            _item('Continue Watching', _tmdb('trakt_ondeck', 'tv', limit), 'leanflix-home-continue'),
            _item('Trending Movies', _tmdb('trending_week', 'movie', limit), 'leanflix-home-trending-movies'),
            _item('Trending TV Shows', _tmdb('trending_week', 'tv', limit), 'leanflix-home-trending-tv'),
            _item('Movie Watchlist', _tmdb('trakt_watchlist', 'movie', limit), 'leanflix-home-watchlist-movies'),
        ]
    return [
        _item('Trending Movies', _tmdb('trending_week', 'movie'), 'leanflix-home-trending-movies'),
        _item('Trending TV Shows', _tmdb('trending_week', 'tv'), 'leanflix-home-trending-tv'),
        _item('Popular Movies', _tmdb('popular', 'movie'), 'leanflix-home-popular-movies'),
        _item('Popular TV Shows', _tmdb('popular', 'tv'), 'leanflix-home-popular-tv'),
        _item('Continue Watching', _tmdb('trakt_ondeck', 'tv'), 'leanflix-home-continue'),
        _item('Movie Watchlist', _tmdb('trakt_watchlist', 'movie'), 'leanflix-home-watchlist-movies'),
        _item('TV Watchlist', _tmdb('trakt_watchlist', 'tv'), 'leanflix-home-watchlist-tv'),
    ]


def movies_widgets(tv_mode=False):
    limit = TV_WIDGET_LIMIT if tv_mode else None
    if tv_mode:
        return [
            _item('Trending Movies', _tmdb('trending_week', 'movie', limit), 'leanflix-movies-trending'),
            _item('Popular Movies', _tmdb('popular', 'movie', limit), 'leanflix-movies-popular'),
            _item('Movie Watchlist', _tmdb('trakt_watchlist', 'movie', limit), 'leanflix-movies-watchlist'),
        ]
    return [
        _item('Trending Movies', _tmdb('trending_week', 'movie'), 'leanflix-movies-trending'),
        _item('Popular Movies', _tmdb('popular', 'movie'), 'leanflix-movies-popular'),
        _item('In Theatres', _tmdb('now_playing', 'movie'), 'leanflix-movies-theatres'),
        _item('Upcoming', _tmdb('upcoming', 'movie'), 'leanflix-movies-upcoming'),
        _item('Top Rated', _tmdb('top_rated', 'movie'), 'leanflix-movies-top'),
        _item('Movie Watchlist', _tmdb('trakt_watchlist', 'movie'), 'leanflix-movies-watchlist'),
        _item('In Progress', _tmdb('trakt_inprogress', 'movie'), 'leanflix-movies-inprogress'),
    ]


def tv_widgets(tv_mode=False):
    limit = TV_WIDGET_LIMIT if tv_mode else None
    if tv_mode:
        return [
            _item('Trending TV Shows', _tmdb('trending_week', 'tv', limit), 'leanflix-tv-trending'),
            _item('Popular TV Shows', _tmdb('popular', 'tv', limit), 'leanflix-tv-popular'),
            _item('TV Watchlist', _tmdb('trakt_watchlist', 'tv', limit), 'leanflix-tv-watchlist'),
        ]
    return [
        _item('Trending TV Shows', _tmdb('trending_week', 'tv'), 'leanflix-tv-trending'),
        _item('Popular TV Shows', _tmdb('popular', 'tv'), 'leanflix-tv-popular'),
        _item('Airing Today', _tmdb('airing_today', 'tv'), 'leanflix-tv-airing'),
        _item('On The Air', _tmdb('on_the_air', 'tv'), 'leanflix-tv-ontheair'),
        _item('Top Rated', _tmdb('top_rated', 'tv'), 'leanflix-tv-top'),
        _item('TV Watchlist', _tmdb('trakt_watchlist', 'tv'), 'leanflix-tv-watchlist'),
        _item('Next Episodes', _tmdb('trakt_nextepisodes', 'tv'), 'leanflix-tv-next'),
    ]


def lean_submenu():
    """Replace default Videos / Music / Pictures submenu with movies/TV/search."""
    return [
        {
            'label': 'Movies',
            'icon': 'special://skin/extras/icons/film.png',
            'path': 'ActivateWindow(videos,%s?info=dir_movie,return)' % TMDBH,
            'target': '',
            'guid': 'leanflix-sub-movies',
        },
        {
            'label': 'TV Shows',
            'icon': 'special://skin/extras/icons/tv.png',
            'path': 'ActivateWindow(videos,%s?info=dir_tv,return)' % TMDBH,
            'target': '',
            'guid': 'leanflix-sub-tv',
        },
        {
            'label': 'Search',
            'icon': 'special://skin/extras/icons/search.png',
            'path': 'ReplaceWindow(1105)',
            'target': '',
            'guid': 'leanflix-sub-search',
        },
        {
            'label': 'Settings',
            'icon': 'special://skin/extras/icons/settings.png',
            'path': 'ActivateWindow(1170)',
            'target': '',
            'guid': 'leanflix-sub-settings',
        },
    ]


def _fen_style_player(name, plugin_id, priority):
    # Red Light / Fen Light AM are Fen-family scrapers. playback.media is the
    # current Fen router (verified via Red Light sources.py / Fen v33+).
    play_movie = (
        'plugin://%s/?mode=playback.media&media_type=movie'
        '&tmdb_id={tmdb}&imdb_id={imdb}&query={title}&title={title}&year={year}'
        '&autoplay=true'
    ) % plugin_id
    play_episode = (
        'plugin://%s/?mode=playback.media&media_type=episode'
        '&tmdb_id={tmdb}&imdb_id={imdb}&query={showname}&year={year}'
        '&season={season}&episode={episode}&ep_name={title}&premiered={firstaired}'
        '&autoplay=true'
    ) % plugin_id
    return {
        'name': name,
        'plugin': plugin_id,
        'priority': priority,
        'is_resolvable': 'false',
        'play_movie': play_movie,
        'play_episode': play_episode,
    }


def _nodes_dir():
    root = kodi.translate_path('special://profile/addon_data')
    return os.path.join(root, NODES_SUBDIR)


def _players_dir():
    root = kodi.translate_path('special://profile/addon_data')
    return os.path.join(root, PLAYERS_SUBDIR)


def _dump_json(path, payload):
    text = json.dumps(payload, indent=2, ensure_ascii=False) + '\n'
    if not kodi.write_text(path, text):
        raise RuntimeError('Could not write %s' % path)
    kodi.log('Wrote preset %s' % path)


def _backup_if_present(path):
    if not kodi.file_exists(path):
        return
    stamp = time.strftime('%Y%m%d-%H%M%S')
    backup = '%s.leanflix-bak-%s' % (path, stamp)
    try:
        kodi.copy_file(path, backup)
        kodi.log('Backed up %s' % path)
    except Exception as exc:
        kodi.log('Backup skipped for %s: %s' % (path, exc), xbmc.LOGWARNING)


def _write_skinvariables_nodes(tv_mode=False):
    dest = _nodes_dir()
    kodi.ensure_dir(dest)
    files = {
        'skinvariables-shortcut-homewidgets.json': home_widgets(tv_mode=tv_mode),
        'skinvariables-shortcut-1101widgets.json': movies_widgets(tv_mode=tv_mode),
        'skinvariables-shortcut-1102widgets.json': tv_widgets(tv_mode=tv_mode),
        'skinvariables-shortcut-homesubmenu.json': lean_submenu(),
        'skinvariables-shortcut-1101submenu.json': lean_submenu(),
        'skinvariables-shortcut-1102submenu.json': lean_submenu(),
    }
    written = []
    for name, payload in files.items():
        path = os.path.join(dest, name)
        _backup_if_present(path)
        _dump_json(path, payload)
        written.append(name)
    return written


def _write_players():
    if not kodi.is_addon_installed(TMDBHELPER_ID):
        return []
    dest = _players_dir()
    kodi.ensure_dir(dest)
    specs = (
        ('leanflix.redlight.json', 'Red Light', REDLIGHT_ID, 40),
        ('leanflix.fenlightam.json', 'Fen Light AM', 'plugin.video.fenlightam', 60),
        ('leanflix.fenlight.json', 'Fen Light', 'plugin.video.fenlight', 80),
    )
    written = []
    for filename, name, plugin_id, priority in specs:
        if not kodi.is_addon_installed(plugin_id):
            continue
        path = os.path.join(dest, filename)
        _dump_json(path, _fen_style_player(name, plugin_id, priority))
        written.append(filename)
    return written


def _default_player_filename():
    vod_id = installer.resolve_vod_id()
    mapping = {
        REDLIGHT_ID: 'leanflix.redlight.json',
        'plugin.video.fenlightam': 'leanflix.fenlightam.json',
        'plugin.video.fenlight': 'leanflix.fenlight.json',
    }
    if vod_id in mapping:
        return mapping[vod_id]
    for addon_id in (REDLIGHT_ID,) + FEN_CANDIDATE_IDS:
        if kodi.is_addon_installed(addon_id):
            return mapping[addon_id]
    return None


def _configure_tmdbhelper_players():
    if not kodi.is_addon_installed(TMDBHELPER_ID):
        return False
    try:
        helper = xbmcaddon.Addon(TMDBHELPER_ID)
    except RuntimeError:
        return False
    # 0 = Never look up / play from the local Kodi library (no library in LeanFlix)
    pairs = [
        ('use_kodi_local_db', '0'),
        ('default_player_kodi', '0'),
        ('widgets_nextpage', 'false'),
    ]
    for key, value in pairs:
        try:
            helper.setSetting(key, value)
        except Exception as exc:
            kodi.log('TMDb Helper setSetting(%s) failed: %s' % (key, exc), xbmc.LOGWARNING)
    player = _default_player_filename()
    if player:
        for key in ('default_player_movies', 'default_player_episodes'):
            try:
                helper.setSetting(key, player)
            except Exception as exc:
                kodi.log('TMDb Helper setSetting(%s) failed: %s' % (key, exc), xbmc.LOGWARNING)
    return True


def _configure_tmdbhelper_tv_mode():
    """Lower artwork cost so widgets do not stall a Sony / built-in smart TV."""
    if not kodi.is_addon_installed(TMDBHELPER_ID):
        return False
    try:
        helper = xbmcaddon.Addon(TMDBHELPER_ID)
    except RuntimeError:
        return False
    # artwork_quality: 0 Highest, 1 High, 2 Medium, 3 Low, 4 Original (huge files)
    for key, value in (
        ('artwork_quality', '3'),
        ('fanarttv_lookup', 'false'),
        ('use_online_ratings', 'false'),
        ('genre_fanart', 'false'),
        ('provider_fanart', 'false'),
        ('pagemulti_tmdb', '1'),
        ('pagemulti_trakt', '1'),
        ('max_threads', '10'),
    ):
        try:
            helper.setSetting(key, value)
        except Exception as exc:
            kodi.log('TMDb Helper TV setSetting(%s) failed: %s' % (key, exc), xbmc.LOGWARNING)
    return True


def _configure_kodi_tv_settings():
    for setting, value in (
        ('videoplayer.hqscalers', 0),
        ('lookandfeel.enablerssfeeds', False),
    ):
        result = kodi.jsonrpc('Settings.SetSettingValue', {
            'setting': setting,
            'value': value,
        })
        if not kodi.jsonrpc_ok(result):
            kodi.log('Kodi setting %s failed: %s' % (setting, result), xbmc.LOGWARNING)


def _current_skin_id():
    result = kodi.jsonrpc('Settings.GetSettingValue', {'setting': 'lookandfeel.skin'})
    try:
        return result['result']['value']
    except (KeyError, TypeError):
        return ''


def _configure_hub_switcher(tv_mode=False):
    """Movies + TV Shows hubs on; Live TV / extra hubs off. Search + Settings stay."""
    if _current_skin_id() != SKIN_ID:
        kodi.log('Skip hub switcher strings; current skin is not %s' % SKIN_ID, xbmc.LOGWARNING)
        return
    kodi.skin_set_string('HomeSwitcher.1101.Toggle', 'true')
    kodi.skin_set_string('HomeSwitcher.1101.Name', 'Movies')
    kodi.skin_set_string('HomeSwitcher.1101.Icon', 'special://skin/extras/icons/film.png')
    kodi.skin_set_string('HomeSwitcher.1102.Toggle', 'true')
    kodi.skin_set_string('HomeSwitcher.1102.Name', 'TV Shows')
    kodi.skin_set_string('HomeSwitcher.1102.Icon', 'special://skin/extras/icons/tv.png')
    if tv_mode:
        # Spotlight fanart is expensive on weak SoCs
        kodi.skin_reset('HomeSwitcher.Home.Spotlight.Path')
        kodi.skin_reset('HomeSwitcher.Home.Spotlight.Target')
        kodi.skin_reset('HomeSwitcher.Home.Spotlight.Label')
    else:
        kodi.skin_set_string(
            'HomeSwitcher.Home.Spotlight.Path',
            _tmdb('trending_week', 'movie'),
        )
        kodi.skin_set_string('HomeSwitcher.Home.Spotlight.Target', 'videos')
        kodi.skin_set_string('HomeSwitcher.Home.Spotlight.Label', 'Trending Movies')
    kodi.skin_reset(LIVE_TV_TOGGLE)
    for hub in ('1103', '1104', '1106', '1108'):
        kodi.skin_reset('HomeSwitcher.%s.Toggle' % hub)
    kodi.skin_set_bool('HomeSwitcher.DisableSearch', False)


def _configure_fuse_tv_performance():
    """Fuse 3 first-run enables blur + crop; both hammer a Sony TV CPU."""
    if _current_skin_id() != SKIN_ID:
        return
    kodi.skin_reset('TMDbHelper.EnableBlur')
    kodi.skin_reset('TMDbHelper.EnableCrop')
    kodi.skin_reset('Background.ExtraFanart')
    kodi.skin_reset('SeasonalTheme.Enable')
    kodi.skin_set_bool('Background.DisableVideo', True)


def _rebuild_skinvariables():
    if not kodi.is_addon_installed(SKINVARIABLES_ID):
        kodi.log('script.skinvariables missing; skin will rebuild on next Fuse load', xbmc.LOGWARNING)
        return False
    # Fuse 3 generator is shortcuts/skinvariables-generator.json (no template suffix)
    kodi.execute_builtin('RunScript(script.skinvariables,action=buildtemplate,force)', True)
    kodi.sleep_ms(1500)
    kodi.execute_builtin('ReloadSkin()', True)
    return True


def tmdbhelper_trakt_authorized():
    if not kodi.is_addon_installed(TMDBHELPER_ID):
        return False
    try:
        token = xbmcaddon.Addon(TMDBHELPER_ID).getSetting('trakt_token')
    except RuntimeError:
        return False
    return bool(token and token.strip())


def open_tmdbhelper_trakt():
    if not kodi.is_addon_installed(TMDBHELPER_ID):
        kodi.ok(kodi.localized(30000), kodi.localized(30077))
        return False
    kodi.ok(kodi.localized(30074), kodi.localized(30075))
    kodi.execute_builtin('RunScript(%s,authenticate_trakt)' % TMDBHELPER_ID, True)
    return True


def apply_netflix_home(prompt=True, tv_mode=None):
    heading = kodi.localized(30000)
    if not kodi.is_addon_installed(SKIN_ID):
        kodi.ok(heading, kodi.localized(30073))
        return False
    if prompt and not kodi.yesno(heading, kodi.localized(30071)):
        return False

    if tv_mode is None:
        tv_mode = kodi.yesno(heading, kodi.localized(30080))

    if not kodi.is_addon_enabled(SKIN_ID):
        kodi.set_addon_enabled(SKIN_ID, True)
        kodi.sleep_ms(800)

    try:
        nodes = _write_skinvariables_nodes(tv_mode=tv_mode)
        players = _write_players()
        _configure_tmdbhelper_players()
        if tv_mode:
            _configure_tmdbhelper_tv_mode()
            _configure_kodi_tv_settings()
            _configure_fuse_tv_performance()
        _configure_hub_switcher(tv_mode=tv_mode)
        _rebuild_skinvariables()
    except Exception as exc:
        kodi.log('Home preset failed: %s' % exc, xbmc.LOGERROR)
        kodi.ok(heading, kodi.localized(30078) % str(exc))
        return False

    if tv_mode:
        kodi.notify(heading, kodi.localized(30081))
        kodi.log('Applied TV home (%s nodes, %s players)' % (len(nodes), len(players)))
    else:
        kodi.notify(heading, kodi.localized(30072))
        kodi.log('Applied Netflix home (%s nodes, %s players)' % (len(nodes), len(players)))

    if not tmdbhelper_trakt_authorized():
        if kodi.yesno(heading, kodi.localized(30076)):
            open_tmdbhelper_trakt()
    return True


def apply_tv_performance(prompt=True):
    heading = kodi.localized(30000)
    if prompt and not kodi.yesno(heading, kodi.localized(30082)):
        return False
    return apply_netflix_home(prompt=False, tv_mode=True)
