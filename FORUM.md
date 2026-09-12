# Ready-to-post reply for Anki forums

Suggested threads:

- https://forums.ankiweb.net/t/how-to-get-tts-working-on-linux-ubuntu/52905
- https://forums.ankiweb.net/t/ignore-built-in-tts-code-when-running-in-linux/27426

---

Anki on Linux has no built-in TTS engine, so native `{{tts lang:Field}}` / `[anki:tts]` tags fail with `no players found for TTSTag(...)`. The manual already points at the sample gTTS add-on (`391644525`). That works for a basic `{{tts en_US voices=gTTS:Front}}` setup, but it drops the player after you switch profiles, has no offline fallback, and does not help much if your templates still name Apple or Microsoft voices from another OS.

I hit this on Arch/Omarchy and packaged a drop-in Linux player:

https://github.com/argrig666/anki-linux-tts-player

Install `linux_tts_player.ankiaddon` from the Releases page (**Tools → Add-ons → Install from file…**), restart Anki, and existing `{{tts it_IT:Front}}` tags speak. Named Windows/macOS voices fall back to the first gTTS voice for that language. If Google TTS is down, install `espeak-ng` and it keeps working.

There is also a small upstream fix so the official gTTS sample survives profile switches: https://github.com/ankitects/anki-addons/pull/40
