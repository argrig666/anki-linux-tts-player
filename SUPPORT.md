# Support & Troubleshooting: Linux TTS Player

## Quick checks

1. Confirm `mpv` is installed and can play audio on your system.
2. Enable `"debug_log": true` in the add-on config, restart Anki, review a card with a `{{tts}}` tag, then inspect:
   `~/.local/share/Anki2/addons21/linux_tts_player/user_files/debug.log`
3. Confirm the log shows `Synthesized Edge TTS (...)` or `Cache hit (edge/...)`.

## Wrong voice quality (male / robotic / “Google Translate” sounding)

**Symptom:** Cards that previously used a high-quality neural voice suddenly sound lower quality, often with a different gender or accent. Some older cards may still sound correct.

**Cause (October 2026):** Microsoft changed the Edge Read Aloud synthesis handshake. Bundled `edge-tts` **7.2.8 and earlier** receive `WSServerHandshakeError: 403 Invalid response status`. The add-on then falls back to Google Translate TTS (gTTS). Because the cache key used to omit the synthesis engine, fallback audio could be stored under the neural voice’s cache identity and keep playing after Edge recovered.

**Fix:**
1. Upgrade to add-on **v1.1.0+** (vendors `edge-tts>=7.3.0`, which restores neural synthesis).
2. Clear the local TTS cache, then restart Anki:
   ```bash
   rm -f ~/.local/share/Anki2/addons21/linux_tts_player/user_files/cache/*
   ```
3. Re-review affected cards so audio regenerates with Edge Neural voices.

From v1.1.0 onward, cache keys include the engine (`edge` / `gtts` / `espeak`), so a temporary fallback cannot overwrite a neural cache entry.

## Edge TTS still failing after upgrade

1. Confirm the bundled library version is at least 7.3.0:
   ```bash
   python3 -c "import sys; sys.path.insert(0, '$HOME/.local/share/Anki2/addons21/linux_tts_player/vendor'); from importlib.metadata import version; print(version('edge-tts'))"
   ```
2. Restart Anki after upgrading (Python keeps the old module loaded until restart).
3. Check upstream `edge-tts` releases if Microsoft changes the endpoint again: https://github.com/rany2/edge-tts/releases

## Reporting an issue

Open an issue: https://github.com/argrig666/anki-linux-tts-player/issues

Include:
1. Anki version (**Help → About**)
2. Linux distribution and desktop environment
3. Relevant lines from `user_files/debug.log`
4. Bundled `edge-tts` version (command above)
5. A minimal `{{tts}}` tag / field text that fails
