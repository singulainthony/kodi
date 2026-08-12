# Arctic Fuse 3 — LeanFlix home preset

Arctic Fuse 3 default home rows are **local Kodi library playlists** (`special://skin/extras/playlists/*.xsp`). LeanFlix has no video library — VOD is Red Light — so those rows stay empty even when Search works.

The wizard now **writes the TMDb Helper widget JSON** Fuse 3 actually reads. Re-apply any time a skin update resets the home.

**Skin ID:** `skin.arctic.fuse.3`  
**Widgets:** TMDb Helper (`plugin.video.themoviedb.helper`)  
**Config dir:** `userdata/addon_data/script.skinvariables/nodes/skin.arctic.fuse.3/`

## Apply with the wizard (preferred)

On an already-installed box:

1. Update / reinstall `install/script.leanflix.wizard-1.0.2.zip`
2. **Program add-ons → LeanFlix Wizard**
3. **Apply Netflix home widgets**  
   (or **Setup checklist → Apply Netflix home widgets**)
4. If Continue Watching / watchlists are empty: checklist → **Authorize Trakt in TMDb Helper** (this is *not* the Red Light Trakt login), then re-apply or **Reload skin**
5. Play a title → choose **Red Light** if asked (wizard also writes a TMDb Helper player + sets it as default)

After a fresh core install the wizard offers the same preset once the skin switches.

## What the preset writes

| File | Role |
| --- | --- |
| `skinvariables-shortcut-homewidgets.json` | Home hub Netflix rows |
| `skinvariables-shortcut-1101widgets.json` | Movies hub |
| `skinvariables-shortcut-1102widgets.json` | TV Shows hub |
| `skinvariables-shortcut-homesubmenu.json` | Home submenu (Movies / TV / Search / Settings) |
| `skinvariables-shortcut-1101submenu.json` | Movies hub submenu |
| `skinvariables-shortcut-1102submenu.json` | TV Shows hub submenu |

Copies of these JSON files live in `skin-presets/arctic-fuse-3/` for manual copy.

Hub switcher (skin strings):

- **On:** Home, Movies (`HomeSwitcher.1101`), TV Shows (`HomeSwitcher.1102`), Search (1105), Settings (1170)
- **Off:** Live TV (`HomeSwitcher.1107.Toggle` reset), extra custom hubs 1103/1104, Next Aired 1106, Add-ons 1108

## Widget plugin:// paths (TMDb Helper, current)

`type=` is a legacy alias; current code remaps it to `tmdb_type=`. The preset uses `tmdb_type`.

| Row | Path | Needs Trakt? |
| --- | --- | --- |
| Trending Movies | `plugin://plugin.video.themoviedb.helper/?info=trending_week&tmdb_type=movie&nextpage=false&widget=true` | No |
| Trending TV | `…?info=trending_week&tmdb_type=tv&nextpage=false&widget=true` | No |
| Popular Movies | `…?info=popular&tmdb_type=movie&nextpage=false&widget=true` | No |
| Popular TV | `…?info=popular&tmdb_type=tv&nextpage=false&widget=true` | No |
| In Theatres | `…?info=now_playing&tmdb_type=movie&nextpage=false&widget=true` | No |
| Upcoming | `…?info=upcoming&tmdb_type=movie&nextpage=false&widget=true` | No |
| Airing Today | `…?info=airing_today&tmdb_type=tv&nextpage=false&widget=true` | No |
| On The Air | `…?info=on_the_air&tmdb_type=tv&nextpage=false&widget=true` | No |
| Top Rated | `…?info=top_rated&tmdb_type=movie` or `tmdb_type=tv` | No |
| Continue Watching | `…?info=trakt_ondeck&tmdb_type=tv&nextpage=false&widget=true` | Yes, in **TMDb Helper** |
| Movie Watchlist | `…?info=trakt_watchlist&tmdb_type=movie&nextpage=false&widget=true` | Yes |
| TV Watchlist | `…?info=trakt_watchlist&tmdb_type=tv&nextpage=false&widget=true` | Yes |
| In Progress (movies) | `…?info=trakt_inprogress&tmdb_type=movie&nextpage=false&widget=true` | Yes |
| Next Episodes | `…?info=trakt_nextepisodes&tmdb_type=tv&nextpage=false&widget=true` | Yes |

Trending / Popular are first on Home so the wall is never blank before Trakt.

## Manual click path (if you prefer the GUI)

1. **Skin settings → Shortcuts → Customise shortcuts**
2. Select **Home** → **Widgets** → add / edit rows
3. Source: **TMDb Helper** → Movies / TV lists → Trending This Week, Popular, etc.
4. Enable custom hubs **1101** and **1102**, rename them **Movies** and **TV Shows**
5. Disable **Live TV / PVR** and **Add-ons** hubs
6. Back out to Home (Fuse rebuilds from the JSON)

Authorize Trakt in TMDb Helper:

**Add-ons → TMDb Helper → Settings → API Keys / Trakt → Authenticate**  
or wizard checklist → **Authorize Trakt in TMDb Helper**

## Playback

Selecting a widget title uses TMDb Helper’s player:

1. Wizard writes `userdata/addon_data/plugin.video.themoviedb.helper/players/leanflix.redlight.json`
2. Sets default movie + episode player to that file
3. Sets “play local Kodi library” to **Never** (no library)

Player URL (Fen-family `playback.media`, used by Red Light):

`plugin://plugin.video.redlight/?mode=playback.media&media_type=movie&tmdb_id={tmdb}&…`

If Fuse still asks, pick **Red Light**. Fen Light AM gets a player file only if that add-on is installed.

## After a skin update

Re-run **LeanFlix Wizard → Apply Netflix home widgets**. Do not restore a full userdata dump from another device.

## What not to add

- PVR clients, M3U, live TV, sports
- Music / karaoke / radio
- Arcade / RetroArch
- Extra VOD add-ons alongside Red Light
