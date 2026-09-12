Registers a Linux TTS engine so Anki's native `{{tts lang:Field}}` and `[anki:tts]` tags produce audio.

Anki itself only ships TTS on Windows and macOS. This add-on uses Google Translate TTS (gTTS). If that request fails, it falls back to `espeak-ng` when that program is on your PATH.

Templates that name Apple / Android / Microsoft voices still work: Anki uses the first gTTS voice for that language.

Restart Anki after installing. To list voices, put `{{tts-voices:}}` on a card template.

If you also have the official "gTTS text to speech support" add-on (`391644525`) enabled, disable one of them to avoid duplicate voices.
