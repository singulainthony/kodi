# LeanFlix install guide (Kodi 21 Omega)

LeanFlix is a **small** movies/TV setup: Arctic Fuse 3 + **Red Light** (Real-Debrid VOD from The Red Repo) + CocoScrapers, authorized with **Real-Debrid** and **Trakt**. Fen Light AM is used only if The Red Repo still lists it. No live TV, music, or arcade.

Time on a fresh Kodi 21 box: about 10 minutes once you have RD + Trakt accounts.

## 1. Install Kodi 21 Omega

Use the official Kodi 21 build for your device (Fire TV / Android TV / Shield / desktop).

## 2. Enable third-party add-ons

1. Open **Settings** (gear).
2. **System → Add-ons**
   - Turn **Unknown sources** **On**. Confirm the warning.
   - Set **Updates** / **Update official add-ons from** to **Any repositories**.
3. Optional but useful: **Settings → Interface → Screensaver** off while installing.

## 3. Install LeanFlix (File Manager source — best on a TV remote)

No Downloader app needed. Add a short HTTP source, then install the zip from it.

### A. File Manager source (recommended on TV)

1. **Settings → File Manager → Add source**
2. Enter this URL (or the short link below):

   `https://singulainthony.github.io/kodi/repo/`

   Short link (easier to type): **`https://tinyurl.com/22v2xar3`**

3. Name the source **LeanFlix** → OK.
4. **Add-ons → open-box icon → Install from zip file** → **LeanFlix**
5. Select **`script.leanflix.wizard-1.0.2.zip`** → install.
6. Run **Program add-ons → LeanFlix Wizard**.

### B. USB / local copy

1. Copy `install/script.leanflix.wizard-1.0.2.zip` to USB or Downloads.
2. **Install from zip file** → browse to the zip → install.
3. Run **Program add-ons → LeanFlix Wizard**.

### C. Repository zip (then install wizard from the LeanFlix repo)

1. From the same File Manager source, install **`repository.leanflix-1.0.0.zip`**.
2. **Install from repository → LeanFlix Repo → Program add-ons → LeanFlix Wizard**.

The repo’s `<info>` / `<datadir>` point at:

`https://raw.githubusercontent.com/singulainthony/kodi/main/zips/`

## 4. Run the wizard

1. Open **LeanFlix Wizard**.
2. Choose **Install core components**. Confirm Kodi’s install prompts.
3. The wizard:
   - Adds File Manager sources: jurialmunkey, redwizard, cocojoe
   - Installs those three upstream repositories
   - Installs **Arctic Fuse 3**, **Red Light** (`plugin.video.redlight`), **CocoScrapers**
   - Offers to switch the skin to Arctic Fuse 3 (choose **Yes** / keep skin)
   - Offers **Apply Netflix home widgets** (TMDb Helper rows — home is empty until this runs)
4. Already-installed add-ons are skipped.

If Red Light is missing, install it manually:

**Add-ons → Install from repository → The Red Repo → Video add-ons → Red Light**

Then re-run the checklist. Fen Light AM is a fallback only if that catalog still lists it.

## 5. Authorize Real-Debrid

1. Wizard → **Setup checklist → Authorize Real-Debrid** (opens Fen settings).
2. Red Light → **Settings → Accounts → Real-Debrid → Authorize**.
3. On a phone/computer open [https://real-debrid.com/device](https://real-debrid.com/device) and enter the code the add-on shows.
4. Wait until Fen reports success.

A paid Real-Debrid account is required. Free hosters are not the point of this build.

## 6. Authorize Trakt (two places)

Red Light Trakt is for scrobbling / lists **inside the VOD add-on**. Home widgets read Trakt from **TMDb Helper**.

1. Checklist → **Authorize Trakt** → Red Light → **Settings → Accounts → Trakt**.
2. Checklist → **Authorize Trakt in TMDb Helper** (device login on [trakt.tv](https://trakt.tv)).
3. Re-apply **Apply Netflix home widgets** or **Reload skin** so Continue Watching / watchlists fill.

## 7. Scrapers / providers

**Red Light** uses its own Real-Debrid providers — authorizing RD is enough.

If Fen Light AM is installed instead:

1. Checklist → **Enable scrapers / providers**.
2. Fen → **Settings → Provider / Scrapers**:
   - **Enable External Scrapers**
   - **Choose External Scrapers Module** → **CocoScrapers**
3. The wizard tries to write these settings automatically; always confirm in the UI.

## 8. Skin widgets (Netflix home)

The wizard applies this. To re-apply on an existing install:

**LeanFlix Wizard → Apply Netflix home widgets**

Manual click path and exact `plugin://` URLs: [../skin-presets/README.md](../skin-presets/README.md).

Default Fuse 3 home is the local library — it will stay blank until the preset (or a manual TMDb Helper widget edit) runs.

## Upstream sources (not bundled)

| Piece | Source | Add-on ID (verified 2026-08) |
| --- | --- | --- |
| Skin repo | https://jurialmunkey.github.io/repository.jurialmunkey/ | `repository.jurialmunkey` |
| Arctic Fuse 3 | jurialmunkey Omega repo | `skin.arctic.fuse.3` |
| Red Wizard / Red Light | https://repo.redwizard.xyz (`repository.redwizard-1.2.2.zip`) | `plugin.video.redlight` (Fen fallback: `plugin.video.fenlightam` / `plugin.video.fenlight`) |
| CocoJoe | https://cocojoe2411.github.io/ | `repository.cocoscrapers` |
| CocoScrapers | CocoScrapers Repository | `script.module.cocoscrapers` |

LeanFlix does **not** redistribute Fen, CocoScrapers, or Arctic Fuse zips.

## Rebuild zips after edits

```bash
./scripts/package.sh
```

Outputs:

- `zips/addons.xml` + `zips/addons.xml.md5`
- `zips/repository.leanflix/repository.leanflix-1.0.0.zip`
- `zips/script.leanflix.wizard/script.leanflix.wizard-1.0.2.zip`
- `install/` copies of both zips
- `repository.leanflix-1.0.0.zip` at the repo root (first-install convenience)
