# AnkiWeb listing (paste into https://ankiweb.net/shared/upload)

**Title (≤80 chars):** Linux TTS player for native {{tts}} tags

**Tags:** tts linux gtts espeak speech

**Support URL:** https://github.com/argrig666/anki-linux-tts-player/issues

**Min Anki:** 2.1.45+ (or current 24.x/25.x/26.x desktop)

## Description

Anki does not ship a TTS engine on Linux. Cards that use `{{tts lang:Field}}` or `[anki:tts]` then show `no players found for TTSTag(...)`.

This add-on registers a player so those tags speak without editing templates. Cards made on Windows or macOS that name Apple / Android / Microsoft voices still work: Anki uses the first available voice for that language.

How it works:

- Google Translate TTS (gTTS) for online synthesis, with a local cache.
- If gTTS fails, falls back to `espeak-ng` when installed (`sudo pacman -S espeak-ng` or `sudo apt install espeak-ng`).
- Re-registers after you switch Anki profiles (the stock gTTS sample does not).
- Strips HTML and `[sound:]` tags before speaking.

Install, restart Anki, then review as usual. Put `{{tts-voices:}}` on a template if you want to list voices.

Disable the official "gTTS text to speech support" add-on (code `391644525`) if both are enabled.

Source: https://github.com/argrig666/anki-linux-tts-player

Based on Ankitects' gTTS player example. GNU AGPL v3 or later.
