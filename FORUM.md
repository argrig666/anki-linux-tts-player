# Ready-to-post replies for Anki forums

---

## 1. Tailored Reply for: "How to get TTS working on Linux (Ubuntu)?"
**Thread URL:** https://forums.ankiweb.net/t/how-to-get-tts-working-on-linux-ubuntu/52905

```markdown
For anyone arriving here looking for a clean, zero-config solution to the `no players found for TTSTag(...)` error on Linux:

While Anki's official gTTS sample add-on works for basic speech, it has a few known drawbacks:
1. Voices can sound robotic and metallic compared to modern neural TTS.
2. It breaks if you switch Anki profiles in the same session without restarting Anki (because the player registry is cleared on profile close).
3. If cards were created on iOS/macOS or specify Apple/Android/Microsoft voices (e.g. `voices=Apple_...`), they often fail to match.

I packaged an upgraded drop-in add-on that brings **Microsoft Azure / Edge Neural voices** to Linux without requiring any API keys, accounts, or complex setup:

👉 **GitHub Repository:** https://github.com/argrig666/anki-linux-tts-player  
👉 **Latest Release:** [linux_tts_player.ankiaddon (v1.0.0)](https://github.com/argrig666/anki-linux-tts-player/releases/tag/v1.0.0)

### What it does:
- **Ultra-realistic neural voices** across 142 languages (Chinese `zh_CN-XiaoxiaoNeural`, English, Japanese, French, Italian, Spanish, German, etc.).
- **Zero card edits**: Works directly with your existing `{{tts zh_CN:Field}}` tags without touching note templates.
- **Cross-platform voice aliasing**: Automatically maps `Apple_*`, `Microsoft_*`, or Android TTS voice names to matching neural voices.
- **Dynamic synthesis & local caching**: Synthesizes in ~500 ms on first play and caches to disk; repeat reviews play instantly (<1 ms).
- **Multi-tier resilience**: Automatically falls back to Google Translate (gTTS) or offline `espeak-ng` if you're offline.
- **Proper lifecycle handling**: Re-registers automatically when switching profiles (fixing the profile-reopen bug).

### Installation:
1. Download `linux_tts_player.ankiaddon` from the [Releases](https://github.com/argrig666/anki-linux-tts-player/releases) page.
2. In Anki: **Tools → Add-ons → Install from file…**
3. Ensure `mpv` is installed on your system (`sudo apt install mpv` on Ubuntu/Debian, or `sudo pacman -S mpv` on Arch).
4. Restart Anki.
```

---

## 2. Standalone Announcement Topic (for Add-ons category)
**Category:** Add-ons  
**Title:** [Add-on] Linux TTS Player: Zero-Config Microsoft Edge / Azure Neural Voices for native {{tts}} tags

```markdown
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
```
