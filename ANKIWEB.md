# AnkiWeb listing (paste into https://ankiweb.net/shared/upload)

**Title (≤80 chars):** Linux TTS Player: Azure / Edge Neural voices for native {{tts}} tags

**Tags:** tts linux azure edge-tts speech audio

**Support URL:** https://github.com/argrig666/anki-linux-tts-player/issues

**Min Anki:** 23.10+ (tested on current 24.x / 25.x / 26.x desktop)

## Description

Anki does not ship a native TTS engine on Linux. Cards with `{{tts lang:Field}}` or `[anki:tts]` tags fail silently or show `no players found for TTSTag(...)`.

This add-on brings Microsoft's **Azure / Edge Neural Speech** directly to Linux, providing crystal-clear, human-grade neural voices without requiring API keys, cloud accounts, or subscriptions.

### Key Features

- **322 Neural Voices across 142 Locales**: Italian, French, German, Spanish, English, Japanese, Russian, Portuguese, Chinese, and many more.
- **Zero API Keys & Zero Costs**: Connects out-of-the-box via the Microsoft Edge neural service.
- **Universal Tag Normalization**: Automatically resolves any tag format (`it`, `it-IT`, `it_IT`, `ita`).
- **Cross-Platform Voice Aliasing**: Cards created on iOS, macOS, or Android specifying `Apple_*`, `com.google.android.tts-*`, or `Microsoft_*` voice names automatically alias to matching Azure Neural voices.
- **Dynamic Synthesis**: Newly added cards synthesize in ~500 ms on first review and save to a local disk cache. Repeat reviews play instantly (<1 ms).
- **Multi-Tier Resilience**: Automatically falls back to Google Translate (gTTS) or offline `espeak-ng` if offline.
- **Optimized Linux Audio**: Direct, low-latency playback via `mpv` with PipeWire/PulseAudio integration and software gain boost.
- **Survives Profile Switches**: Properly unregisters and re-registers when switching Anki profiles.

### Prerequisites

Install `mpv` on your Linux system:
- Arch / Omarchy: `sudo pacman -S mpv`
- Ubuntu / Debian: `sudo apt install mpv`
- Fedora: `sudo dnf install mpv`

Disable conflicting legacy add-on `391644525` if installed.

Source code & issues: https://github.com/argrig666/anki-linux-tts-player  
GNU AGPL v3.0 or later.
