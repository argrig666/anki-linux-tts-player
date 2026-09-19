# Ready-to-post reply for Anki forums

Suggested threads:
- https://forums.ankiweb.net/t/how-to-get-tts-working-on-linux-ubuntu/52905
- https://forums.ankiweb.net/t/ignore-built-in-tts-code-when-running-in-linux/27426

Or post as a new announcement topic in **Add-ons**:
**Title:** [Add-on] Linux TTS Player: Zero-Config Microsoft Edge / Azure Neural Voices for native {{tts}} tags

---

Hi everyone,

If you use Anki on Linux, you've probably run into the **Linux TTS void**:
- On macOS, Anki hooks cleanly into `say`.
- On Windows, Anki hooks into SAPI and Windows Media Speech.
- **On Linux, Anki ships with no native TTS engine.**

When reviewing shared decks or decks synced from iOS or Android (e.g. language decks containing tags like `{{tts it_IT voices=Apple_Federica_(Premium),com.google.android.tts...:Field}}`), Linux users either get complete silence or have to settle for robotic `espeak`. Existing solutions like HyperTTS or AwesomeTTS are powerful, but often require configuring cloud API keys, paid credits, or custom menus.

To solve this, I created **Linux TTS Player (Edge Neural / Azure Speech)**: a lightweight, self-contained add-on that brings Microsoft's Azure / Edge Neural Speech engines directly to Anki on Linux:

👉 **GitHub Repository:** https://github.com/argrig666/anki-linux-tts-player

### Key Highlights

1. **Ultra-Realistic Neural Voices**: 322 human-grade voices across 142 locales (Italian, French, Spanish, German, English, Russian, Japanese, Portuguese, Chinese, etc.).
2. **Zero API Keys & Zero Sign-ups**: Works out of the box through Microsoft's Edge Speech neural endpoint. No subscriptions or credentials needed.
3. **Transparent Mobile/Desktop Aliasing**: Decks created on iOS, macOS, or Android using `Apple_*`, `com.google.android.tts-*`, or `Microsoft_*` voice names automatically resolve to matching Azure Neural voices.
4. **Dynamic On-The-Fly Synthesis**: When you add or review new cards, audio is generated in ~500 ms and cached locally on disk. All subsequent reviews play instantly (<1 ms).
5. **Multi-Tier Resilience**: Automatically falls back to Google Translate (gTTS) or offline `espeak-ng` if you're offline.
6. **Optimized PipeWire / PulseAudio Playback**: Direct subprocess playback via `mpv` with `--load-scripts=no` (eliminating DBus/MPRIS delays) and a built-in volume boost so speech is crisp over laptop speakers.

### How to Install

- **Release Package**: Download `linux_tts_player.ankiaddon` from the [Releases](https://github.com/argrig666/anki-linux-tts-player/releases) page (**Tools → Add-ons → Install from file…**).
- **From Source**:
  ```bash
  cd ~/.local/share/Anki2/addons21/
  git clone https://github.com/argrig666/anki-linux-tts-player.git linux_tts_player
  ```
- **Prerequisite**: Ensure `mpv` is installed (`sudo pacman -S mpv` or `sudo apt install mpv`).

Feedback and contributions welcome!
