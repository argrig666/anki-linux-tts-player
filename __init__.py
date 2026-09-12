# Copyright: Ankitects Pty Ltd and contributors
# Copyright: argrig666 and contributors
# License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl.html
"""Linux TTS player for Anki's native {{tts}} / [anki:tts] tags.

Anki only ships TTS backends for macOS and Windows. This add-on registers a
player so the same tags work on Linux, including templates that name Apple /
Android / Microsoft voices: if that exact voice is missing, Anki falls back to
the first voice we advertise for the tag's language.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import Future
from dataclasses import dataclass
from typing import cast

from anki.lang import compatMap
from anki.sound import AVTag, TTSTag
from anki.utils import checksum
from aqt import gui_hooks, mw
from aqt.sound import OnDoneCallback, av_player
from aqt.tts import TTSProcessPlayer, TTSVoice
from aqt.utils import tooltip

_ADDON_DIR = os.path.dirname(__file__)
_VENDOR = os.path.join(_ADDON_DIR, "vendor")
_CACHE_DIR = os.path.join(_ADDON_DIR, "user_files", "cache")

if _VENDOR not in sys.path:
    sys.path.insert(0, _VENDOR)

from gtts import gTTS  # noqa: E402
from gtts.lang import tts_langs  # noqa: E402


_HTML_RE = re.compile(r"<[^>]+>")
_SOUND_RE = re.compile(r"\[sound:[^\]]*\]")
_ESPEAK = shutil.which("espeak-ng") or shutil.which("espeak")


def _spoken_text(raw: str) -> str:
    text = _SOUND_RE.sub(" ", raw)
    text = _HTML_RE.sub(" ", text)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
    )
    return re.sub(r"\s+", " ", text).strip()


def _anki_lang(code: str) -> str | None:
    code = code.replace("-", "_")
    if "_" in code:
        head, tail = code.split("_", 1)
        return f"{head}_{tail.upper()}"
    return compatMap.get(code)


def _gtts_lang_for_anki(anki_lang: str) -> str:
    """Map Anki's en_US / it_IT onto a gTTS language tag."""
    langs = tts_langs()
    underscored = anki_lang.replace("-", "_")
    hyphen = underscored.replace("_", "-")
    lower = hyphen.lower()
    if hyphen in langs:
        return hyphen
    if lower in langs:
        return lower
    prefix = underscored.split("_", 1)[0]
    if prefix in langs:
        return prefix
    return prefix


def _espeak_voice(anki_lang: str) -> str:
    lang = anki_lang.replace("-", "_")
    table = {
        "en_US": "en-us",
        "en_GB": "en-gb",
        "zh_CN": "cmn",
        "zh_TW": "cmn",
        "pt_BR": "pt-br",
        "pt_PT": "pt-pt",
    }
    if lang in table:
        return table[lang]
    return lang.split("_", 1)[0].lower()


@dataclass
class LinuxTTSVoice(TTSVoice):
    gtts_lang: str


class LinuxTTSPlayer(TTSProcessPlayer):
    def get_available_voices(self) -> list[TTSVoice]:
        voices: list[TTSVoice] = []
        seen: set[str] = set()
        for code in tts_langs():
            std = _anki_lang(code)
            if not std or std in seen:
                continue
            seen.add(std)
            voices.append(LinuxTTSVoice(name="gTTS", lang=std, gtts_lang=_gtts_lang_for_anki(std)))
        return voices

    def _play(self, tag: AVTag) -> None:
        assert isinstance(tag, TTSTag)
        match = self.voice_for_tag(tag)
        assert match
        voice = cast(LinuxTTSVoice, match.voice)

        text = _spoken_text(tag.field_text)
        self._tmpfile = None
        if not text:
            return

        os.makedirs(_CACHE_DIR, exist_ok=True)
        key = checksum(f"{voice.gtts_lang}-{tag.speed}-{text}")
        mp3_path = os.path.join(_CACHE_DIR, f"{key}.mp3")
        wav_path = os.path.join(_CACHE_DIR, f"{key}.wav")

        if os.path.exists(mp3_path):
            self._tmpfile = mp3_path
            return
        if os.path.exists(wav_path):
            self._tmpfile = wav_path
            return

        try:
            tts = gTTS(
                text=text,
                lang=voice.gtts_lang,
                lang_check=False,
                slow=tag.speed < 1,
            )
            tts.save(mp3_path)
            self._tmpfile = mp3_path
            return
        except Exception as err:
            print(f"linux_tts_player: gTTS failed ({err}); trying espeak")

        if not _ESPEAK:
            raise RuntimeError(
                "gTTS failed and espeak-ng is not installed. "
                "Install espeak-ng with your package manager "
                "(for example: sudo pacman -S espeak-ng, or sudo apt install espeak-ng)."
            )

        speed = max(80, min(350, int(175 * tag.speed)))
        subprocess.run(
            [
                _ESPEAK,
                "-v",
                _espeak_voice(voice.lang),
                "-s",
                str(speed),
                "-w",
                wav_path,
                "--",
                text,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._tmpfile = wav_path

    def _on_done(self, ret: Future, cb: OnDoneCallback) -> None:
        try:
            ret.result()
        except Exception as err:
            print(f"linux_tts_player: {err}")
            tooltip(f"TTS failed: {err}")
            cb()
            return

        tmp = getattr(self, "_tmpfile", None)
        if tmp:
            av_player.insert_file(tmp)
        cb()

    def stop(self) -> None:
        # Synthesis is short; mpv can still be interrupted after insert_file.
        pass


def _register_player() -> None:
    # Anki clears the player registry on profile close. Add-ons are imported
    # only once, so registration must also run on each profile open.
    if mw is not None and not any(
        isinstance(player, LinuxTTSPlayer) for player in av_player.players
    ):
        av_player.players.append(LinuxTTSPlayer(mw.taskman))


gui_hooks.profile_did_open.append(_register_player)
_register_player()
