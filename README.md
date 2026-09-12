# Linux TTS player for Anki

Anki's native `{{tts lang:Field}}` and `[anki:tts]` tags speak on Windows and
macOS. On Linux they do not: there is no built-in voice, so reviews show
`no players found for TTSTag(...)`.

This add-on registers a TTS player so those tags work without rewriting
templates. Cards created on Windows or macOS that name Apple / Android /
Microsoft voices still speak: Anki falls back to the first voice this add-on
advertises for the tag's language.

It is a derivative of Anki's official [gTTS player example](https://github.com/ankitects/anki-addons/tree/main/code/gtts_player)
([AnkiWeb 391644525](https://ankiweb.net/shared/info/391644525)), with the
fixes Linux users actually hit:

- Re-register the player when you switch profiles (Anki clears the player list
  on profile close; add-ons are not re-imported).
- Strip HTML and `[sound:]` tags before synthesis.
- Cache generated audio under `user_files/cache/`.
- Fall back to `espeak-ng` if Google TTS is unreachable.
- Show a tooltip instead of failing the review when both engines fail.

## Install

### From a release (recommended)

1. Download `linux_tts_player.ankiaddon` from [Releases](https://github.com/argrig666/anki-linux-tts-player/releases).
2. In Anki: **Tools → Add-ons → Install from file…** and choose that file.
3. Restart Anki.

If this add-on is later on AnkiWeb, you can instead use **Get Add-ons…** and
paste the code from the AnkiWeb page.

### From source

```sh
git clone https://github.com/argrig666/anki-linux-tts-player.git
cp -a anki-linux-tts-player ~/.local/share/Anki2/addons21/linux_tts_player
```

Restart Anki. Disable the official gTTS add-on (`391644525`) if both are
enabled; they register the same voice name.

## Usage

No template changes are required. Existing tags such as these already work:

```
{{tts it_IT:Front}}
{{tts fr_FR speed=0.8:Front}}
{{tts ja_JP voices=Apple_Otoya,Microsoft_Haruka:Expression}}
[anki:tts lang=en_US]{{Front}}[/anki:tts]
```

To confirm the player loaded, temporarily put `{{tts-voices:}}` on a card
template. You should see `gTTS` listed for many languages.

Optional offline fallback:

```sh
sudo pacman -S espeak-ng    # Arch / Omarchy
sudo apt install espeak-ng  # Debian / Ubuntu
```

gTTS needs network access to `translate.google.com`. The first play of a
phrase downloads an mp3; repeats use the cache.

## Why this exists

Anki's manual already says Linux has no built-in voices and points at add-on
`391644525`. That add-on is a sample: it does not restore itself after a
profile switch, it has no offline fallback, and it surfaces synthesis errors
as a failed play. This package is the same idea, packaged for people who
installed Anki on Linux and just want `{{tts}}` to speak.

A profile-reopen fix for the official sample is in
[ankitects/anki-addons#40](https://github.com/ankitects/anki-addons/pull/40).
Until that is merged and re-uploaded to AnkiWeb, this add-on is the drop-in
Linux player.

## License

GNU AGPL v3 or later. Includes [gTTS](https://github.com/pndurette/gTTS)
(MIT) under `vendor/`.
