# My Anki add-ons

Personal restore list for a fresh Anki Desktop installation.

## Installed add-ons

| Add-on | Anki add-on ID | Status | Notes |
|---|---:|---|---|
| AnkiConnect | `2055492159` | enabled | Required by local automation/scripts. |
| Review Heatmap | `1771074083` | enabled | Review calendar/heatmap. |
| More Overview Stats 2.1 | `2116130837` | enabled | Legacy add-on; its metadata advertises compatibility only through Anki 24.04.1. |
| New Cards Learned Per Day | `90737033` | enabled | Legacy add-on; its metadata advertises compatibility only through Anki 25.09.2. |
| gTTS text to speech support | `391644525` | disabled | Kept installed as a fallback/legacy option. |
| Linux TTS player (Azure / Edge Neural TTS) | local add-on directory: `linux_tts_player` | enabled | This repository; install from the release `.ankiaddon` or clone into `addons21/linux_tts_player`. |
| Pronounce Selected Text | custom add-on directory: `pronounce_selected` | enabled | Personal add-on; source/installer is maintained in the private `anki-pronounce-selected` project. Default shortcut: `Alt+C`. |

## Restore procedure

1. Install Anki Desktop.
2. Open **Tools → Add-ons → Get Add-ons…** and enter each numeric ID above.
3. Install this repository's Linux TTS Player from its latest release, or clone it into the profile's `addons21/linux_tts_player` directory.
4. Restart Anki.
5. Re-check legacy add-ons after each Anki upgrade; if one causes errors, disable it rather than deleting it.

The personal `Pronounce Selected Text` add-on is not an AnkiWeb numeric-ID add-on. Restore it from its packaged `pronounce_selected.ankiaddon` installer or copy the project into `addons21/pronounce_selected`.

For Linux TTS playback, install `mpv`; `espeak-ng` is optional for offline fallback. The Linux TTS Player handles Android/Apple voice names such as `com.google.android.tts-it-it-*` and `Apple_Federica_(Premium)` through its alias resolver.

## Current environment snapshot

- Anki Desktop: 26.08.1
- Platform: Linux
- The collection is not stored in this repository; this file intentionally contains only add-on restore metadata.
