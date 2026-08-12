# LeanFlix

A **lean Real-Debrid + Trakt** pack for **Kodi 21 Omega**: one skin, one VOD add-on, one scraper module. No live TV, music, arcade, or Diggz-style AIO dump.

| Role | Choice |
| --- | --- |
| Skin | Arctic Fuse 3 (`skin.arctic.fuse.3`) via [jurialmunkey](https://jurialmunkey.github.io/repository.jurialmunkey/) |
| VOD | Red Light via [The Red Repo](https://repo.redwizard.xyz) (Fen Light AM if still listed) |
| Scrapers | CocoScrapers via [CocoJoe](https://cocojoe2411.github.io/) |
| Accounts | Real-Debrid + Trakt inside Red Light **and** Trakt inside TMDb Helper (home widgets) |

This repository ships **only**:

- `repository.leanflix/` — tiny Kodi repo that lists the wizard
- `script.leanflix.wizard/` — first-run installer + RD/Trakt checklist + Netflix home preset
- Built zips under `zips/` and `install/`

Upstream Fen / Coco / Fuse zips are **not** redistributed. The wizard downloads them from their own repos.

## Install

See **[docs/INSTALL.md](docs/INSTALL.md)**. Short version:

1. Kodi 21 → Unknown Sources → **Any repositories**
2. Install `install/script.leanflix.wizard-1.0.2.zip` (or the repo zip, then the wizard)
3. Run **LeanFlix Wizard → Install core components**
4. Authorize RD (`real-debrid.com/device`) and Trakt in Red Light (or Fen)
5. Apply **Netflix home widgets** (wizard does this after skin switch, or run it from the main menu)
6. Authorize Trakt **again in TMDb Helper** so Continue Watching / watchlists fill

Already installed and the Fuse 3 home is empty? Update the wizard zip to 1.0.2, then **Apply Netflix home widgets**. Details: **[skin-presets/README.md](skin-presets/README.md)**.

## Rebuild packages

```bash
./scripts/package.sh
```

## Layout

```
repository.leanflix/          Kodi repository add-on
script.leanflix.wizard/       First-run program add-on
zips/                         Repo datadir (addons.xml + versioned zips)
install/                      Convenience zips for “Install from zip file”
docs/INSTALL.md
skin-presets/README.md
skin-presets/arctic-fuse-3/   Fuse 3 skinvariables JSON (manual copy)
scripts/package.py
```
