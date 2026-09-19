# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""Edge Neural TTS for Linux (Azure Speech) in Anki.

Universal Text-to-Speech player for Anki on Linux. Works seamlessly with
ANY native {{tts}} tag in ANY card or language:
- Microsoft Azure / Edge Neural voices for 142 locales (322 voices).
- Zero configuration and zero API keys required.
- Universal language normalization (e.g. it-IT, it_IT, it, ita all resolve).
- Cross-platform voice aliasing: Apple (Apple_*), Android (com.google.android.tts-*),
  and Microsoft (Microsoft_*) voice tags automatically map to matching neural voices.
- Dynamic on-the-fly synthesis on new cards with automatic disk caching.
- Multi-tier resilience: automatic fallback to Google Translate (gTTS) and espeak-ng.
- Low-latency PipeWire / PulseAudio direct playback with volume boost.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import cast

import aqt
from anki.lang import compatMap
from anki.sound import AVTag, TTSTag
from anki.utils import checksum
from aqt import gui_hooks
from aqt.sound import OnDoneCallback, av_player
from aqt.tts import TTSProcessPlayer, TTSVoice, TTSVoiceMatch
from aqt.utils import tooltip

_ADDON_DIR = os.path.dirname(__file__)
_VENDOR = os.path.join(_ADDON_DIR, "vendor")
_CACHE_DIR = os.path.join(_ADDON_DIR, "user_files", "cache")
_CONFIG_PATH = os.path.join(_ADDON_DIR, "config.json")
_LOG_PATH = os.path.join(_ADDON_DIR, "user_files", "debug.log")
_VOICES_PATH = os.path.join(_ADDON_DIR, "voices.json")

if _VENDOR not in sys.path:
    sys.path.insert(0, _VENDOR)

import edge_tts  # noqa: E402
from gtts import gTTS  # noqa: E402
from gtts.lang import tts_langs  # noqa: E402

_HTML_RE = re.compile(r"<[^>]+>")
_SOUND_RE = re.compile(r"\[sound:[^\]]*\]")
_ESPEAK = shutil.which("espeak-ng") or shutil.which("espeak")

# ISO 639-2/3 (3-letter) to ISO 639-1 (2-letter) mappings
ISO_3_TO_2: dict[str, str] = {
    "ita": "it", "fra": "fr", "fre": "fr", "eng": "en", "deu": "de", "ger": "de",
    "spa": "es", "jpn": "ja", "zho": "zh", "chi": "zh", "rus": "ru", "por": "pt",
    "pol": "pl", "nld": "nl", "dut": "nl", "kor": "ko", "ara": "ar", "hin": "hi",
    "tur": "tr", "swe": "sv", "ell": "el", "gre": "el", "heb": "he", "ces": "cs",
    "cze": "cs", "dan": "da", "fin": "fi", "hun": "hu", "nor": "no", "ron": "ro",
    "rum": "ro", "slk": "sk", "slo": "sk", "ukr": "uk", "vie": "vi", "tha": "th",
    "cat": "ca", "ind": "id", "msa": "ms", "may": "ms", "hrv": "hr", "srp": "sr",
}

DEFAULT_LOCALE_MAP: dict[str, str] = {
    "it": "it_IT", "fr": "fr_FR", "en": "en_US", "de": "de_DE", "es": "es_ES",
    "ja": "ja_JP", "zh": "zh_CN", "ru": "ru_RU", "pt": "pt_BR", "pl": "pl_PL",
    "nl": "nl_NL", "ar": "ar_SA", "ko": "ko_KR", "tr": "tr_TR", "uk": "uk_UA",
    "el": "el_GR", "he": "he_IL", "hi": "hi_IN", "sv": "sv_SE", "cs": "cs_CZ",
    "da": "da_DK", "fi": "fi_FI", "hu": "hu_HU", "no": "no_NO", "ro": "ro_RO",
    "th": "th_TH", "vi": "vi_VN", "id": "id_ID", "ms": "ms_MY", "sk": "sk_SK",
    "bg": "bg_BG", "ca": "ca_ES", "hr": "hr_HR", "sr": "sr_RS", "sl": "sl_SI",
}

VOICE_ALIASES: dict[str, dict[str, str]] = {
    "it_IT": {
        "federica": "it-IT-ElsaNeural",
        "emma": "it-IT-IsabellaNeural",
        "alice": "it-IT-ElsaNeural",
        "cosimo": "it-IT-DiegoNeural",
        "diego": "it-IT-DiegoNeural",
        "elsa": "it-IT-ElsaNeural",
        "isabella": "it-IT-IsabellaNeural",
        "giuseppe": "it-IT-GiuseppeMultilingualNeural",
    },
    "fr_FR": {
        "vivienne": "fr-FR-VivienneMultilingualNeural",
        "audrey": "fr-FR-VivienneMultilingualNeural",
        "thomas": "fr-FR-HenriNeural",
        "aurelie": "fr-FR-DeniseNeural",
        "denise": "fr-FR-DeniseNeural",
        "henri": "fr-FR-HenriNeural",
        "eloise": "fr-FR-EloiseNeural",
        "remy": "fr-FR-RemyMultilingualNeural",
    },
    "fr_CA": {
        "sylvie": "fr-CA-SylvieNeural",
        "jean": "fr-CA-JeanNeural",
        "antoine": "fr-CA-AntoineNeural",
        "thierry": "fr-CA-ThierryNeural",
    },
    "en_US": {
        "jenny": "en-US-JennyNeural",
        "guy": "en-US-GuyNeural",
        "aria": "en-US-AriaNeural",
        "samantha": "en-US-JennyNeural",
        "ava": "en-US-AriaNeural",
        "david": "en-US-GuyNeural",
        "zira": "en-US-JennyNeural",
    },
    "en_GB": {
        "sonia": "en-GB-SoniaNeural",
        "ryan": "en-GB-RyanNeural",
        "daniel": "en-GB-RyanNeural",
        "oliver": "en-GB-RyanNeural",
    },
    "ru_RU": {
        "svetlana": "ru-RU-SvetlanaNeural",
        "dmitry": "ru-RU-DmitryNeural",
        "milena": "ru-RU-SvetlanaNeural",
        "yuri": "ru-RU-DmitryNeural",
    },
    "ja_JP": {
        "nanami": "ja-JP-NanamiNeural",
        "keita": "ja-JP-KeitaNeural",
        "kyoko": "ja-JP-NanamiNeural",
        "otoya": "ja-JP-KeitaNeural",
    },
    "pt_BR": {
        "francisca": "pt-BR-FranciscaNeural",
        "antonio": "pt-BR-AntonioNeural",
        "luciana": "pt-BR-FranciscaNeural",
    },
    "zh_CN": {
        "xiaoxiao": "zh-CN-XiaoxiaoNeural",
        "yunxi": "zh-CN-YunxiNeural",
        "tingting": "zh-CN-XiaoxiaoNeural",
    },
}


def _load_config() -> dict:
    if aqt.mw and hasattr(aqt.mw, "addonManager"):
        cfg = aqt.mw.addonManager.getConfig(__name__)
        if isinstance(cfg, dict):
            return cfg
    if os.path.isfile(_CONFIG_PATH):
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _log(msg: str) -> None:
    cfg = _load_config()
    if not cfg.get("debug_log", False):
        return
    try:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def _load_voices_catalog() -> dict[str, list[dict[str, str]]]:
    if os.path.isfile(_VOICES_PATH):
        try:
            with open(_VOICES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _clean_voice_name(name: str) -> str:
    s = name
    for prefix in ["Apple_", "Microsoft_", "Google_"]:
        if s.startswith(prefix):
            s = s[len(prefix):]
    s = re.sub(r"_\([^)]+\)", "", s)
    s = re.sub(r"\(.+?\)", "", s)
    s = re.sub(r"_.*", "", s)
    return s.strip().lower()


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


def _get_lang_candidates(raw_lang: str) -> list[str]:
    raw = raw_lang.strip().replace("-", "_")
    low = raw.lower()
    if low in ISO_3_TO_2:
        low = ISO_3_TO_2[low]

    candidates: list[str] = []
    if "_" in raw:
        prefix, country = raw.split("_", 1)
        std = f"{prefix.lower()}_{country.upper()}"
        candidates.extend([std, f"{prefix.lower()}-{country.upper()}", prefix.lower()])
    else:
        prefix = low
        if prefix in DEFAULT_LOCALE_MAP:
            std = DEFAULT_LOCALE_MAP[prefix]
            candidates.extend([std, prefix, std.replace("_", "-")])
        else:
            candidates.append(prefix)
            if prefix in compatMap:
                std = compatMap[prefix]
                candidates.extend([std, std.replace("_", "-")])

    # Deduplicate preserving order
    seen: set[str] = set()
    out: list[str] = []
    for c in candidates:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _gtts_lang_for_anki(anki_lang: str) -> str:
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


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)


async def _synthesize_edge(text: str, voice_name: str, rate: str, output_path: str) -> None:
    communicate = edge_tts.Communicate(text=text, voice=voice_name, rate=rate)
    await communicate.save(output_path)


@dataclass
class LinuxTTSVoice(TTSVoice):
    edge_voice: str | None = None
    gtts_lang: str | None = None


class LinuxTTSPlayer(TTSProcessPlayer):
    default_rank = 10

    def get_available_voices(self) -> list[TTSVoice]:
        catalog = _load_voices_catalog()
        config = _load_config()
        user_defaults = config.get("default_voices", {})

        voices: list[TTSVoice] = []
        registered_keys: set[tuple[str, str]] = set()

        def add_voice(name: str, lang: str, edge_voice: str | None = None, gtts_code: str | None = None):
            k = (name, lang)
            if k not in registered_keys:
                registered_keys.add(k)
                voices.append(LinuxTTSVoice(name=name, lang=lang, edge_voice=edge_voice, gtts_lang=gtts_code))

        # 1. Register all Azure Neural voices across all 142 locales
        for locale_code, voice_list in catalog.items():
            preferred = user_defaults.get(locale_code)
            sorted_list = sorted(
                voice_list,
                key=lambda v: 0 if v["edge_voice"] == preferred else 1,
            )
            gtts_code = _gtts_lang_for_anki(locale_code)
            short_code = locale_code.split("_")[0].lower()

            for v in sorted_list:
                edge_name = v["name"]
                # Register for standard format (e.g. it_IT)
                add_voice(name=edge_name, lang=locale_code, edge_voice=edge_name, gtts_code=gtts_code)
                # Also register for hyphen format (e.g. it-IT) and short format (e.g. it)
                add_voice(name=edge_name, lang=locale_code.replace("_", "-"), edge_voice=edge_name, gtts_code=gtts_code)
                add_voice(name=edge_name, lang=short_code, edge_voice=edge_name, gtts_code=gtts_code)

        # 2. Register Cross-Platform Voice Aliases
        for locale_code, aliases in VOICE_ALIASES.items():
            gtts_code = _gtts_lang_for_anki(locale_code)
            short_code = locale_code.split("_")[0].lower()
            for alias_name, target_edge in aliases.items():
                add_voice(name=alias_name, lang=locale_code, edge_voice=target_edge, gtts_code=gtts_code)
                add_voice(name=alias_name, lang=locale_code.replace("_", "-"), edge_voice=target_edge, gtts_code=gtts_code)
                add_voice(name=alias_name, lang=short_code, edge_voice=target_edge, gtts_code=gtts_code)

        # 3. Register standard gTTS voices for fallback and remaining languages
        for code in tts_langs():
            prefix = code.split("-")[0].lower()
            std = compatMap.get(prefix) or prefix
            gtts_code = _gtts_lang_for_anki(std)
            add_voice(name="gTTS", lang=std, edge_voice=None, gtts_code=gtts_code)
            add_voice(name="gTTS", lang=code, edge_voice=None, gtts_code=gtts_code)
            add_voice(name="gTTS", lang=prefix, edge_voice=None, gtts_code=gtts_code)

        return voices

    def voice_for_tag(self, tag: TTSTag) -> TTSVoiceMatch | None:
        avail_voices = self.voices()
        candidates = _get_lang_candidates(tag.lang)
        config = _load_config()
        user_defaults = config.get("default_voices", {})

        # Find voices matching language candidates
        pool: list[LinuxTTSVoice] = [
            cast(LinuxTTSVoice, v) for v in avail_voices if v.lang in candidates
        ]

        # If empty, try prefix matching (e.g. 'it' matching 'it_IT')
        if not pool:
            lang_prefix = tag.lang.replace("-", "_").split("_")[0].lower()
            pool = [
                cast(LinuxTTSVoice, v)
                for v in avail_voices
                if v.lang.lower().startswith(lang_prefix)
            ]

        # If still empty, fall back to super()
        if not pool:
            match = super().voice_for_tag(tag)
            if match and match.rank <= -100:
                return TTSVoiceMatch(voice=match.voice, rank=-10)
            return match

        rank = self.default_rank

        # Try matching requested voices
        for req in tag.voices:
            # A. Exact name match in pool
            for v in pool:
                if v.name == req or v.edge_voice == req:
                    return TTSVoiceMatch(voice=v, rank=rank)

            # B. Cleaned name & alias matching
            clean = _clean_voice_name(req)
            for cand in candidates:
                if cand in VOICE_ALIASES and clean in VOICE_ALIASES[cand]:
                    target_edge = VOICE_ALIASES[cand][clean]
                    for v in pool:
                        if v.edge_voice == target_edge:
                            return TTSVoiceMatch(voice=v, rank=rank)

            # C. Substring matching in pool
            for v in pool:
                v_clean = _clean_voice_name(v.name)
                if clean == v_clean or (len(clean) >= 3 and clean in (v.edge_voice or "").lower()):
                    return TTSVoiceMatch(voice=v, rank=rank)

            # D. Android voice pattern
            if "android.tts" in req.lower():
                return TTSVoiceMatch(voice=pool[0], rank=rank)

            rank -= 1

        # Check user preferred voice for language
        for cand in candidates:
            if cand in user_defaults:
                pref = user_defaults[cand]
                for v in pool:
                    if v.edge_voice == pref:
                        return TTSVoiceMatch(voice=v, rank=-10)

        # Fall back to first available voice in pool
        return TTSVoiceMatch(voice=pool[0], rank=-10)

    def _play(self, tag: AVTag) -> None:
        assert isinstance(tag, TTSTag)
        match = self.voice_for_tag(tag)
        assert match
        voice = cast(LinuxTTSVoice, match.voice)

        text = _spoken_text(tag.field_text)
        if not text:
            return

        if self._terminate_flag:
            return

        os.makedirs(_CACHE_DIR, exist_ok=True)
        voice_id = voice.edge_voice or voice.gtts_lang or voice.name
        speed_key = round(tag.speed, 2)
        key = checksum(f"{voice_id}-{speed_key}-{text}")
        mp3_path = os.path.join(_CACHE_DIR, f"{key}.mp3")
        wav_path = os.path.join(_CACHE_DIR, f"{key}.wav")

        audio_path: str | None = None

        if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 0:
            audio_path = mp3_path
            _log(f"Cache hit ({voice_id}): '{text}'")
        elif os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
            audio_path = wav_path
            _log(f"Cache hit ({voice_id}): '{text}'")
        else:
            # 1. Attempt Microsoft Azure / Edge Neural TTS
            if voice.edge_voice:
                try:
                    rate_pct = int((tag.speed - 1.0) * 100)
                    rate_str = f"{rate_pct:+d}%"
                    t0 = time.time()
                    _run_async(_synthesize_edge(text, voice.edge_voice, rate_str, mp3_path))
                    if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 0:
                        audio_path = mp3_path
                        dt = round((time.time() - t0) * 1000)
                        _log(f"Synthesized Edge TTS ({voice.edge_voice}, {dt}ms): '{text}'")
                except Exception as err:
                    _log(f"Edge TTS ({voice.edge_voice}) failed ({err}); trying gTTS fallback...")

            # 2. Attempt Google Translate TTS fallback
            if not audio_path:
                gtts_code = voice.gtts_lang or _gtts_lang_for_anki(voice.lang)
                if gtts_code:
                    try:
                        tts = gTTS(
                            text=text,
                            lang=gtts_code,
                            lang_check=False,
                            slow=tag.speed < 1,
                        )
                        tts.save(mp3_path)
                        if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 0:
                            audio_path = mp3_path
                            _log(f"Synthesized gTTS ({gtts_code}): '{text}'")
                    except Exception as err:
                        _log(f"gTTS fallback failed ({err}); trying espeak...")

            # 3. Attempt offline espeak fallback
            if not audio_path and _ESPEAK:
                try:
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
                    if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                        audio_path = wav_path
                        _log(f"Synthesized espeak-ng: '{text}'")
                except Exception as err:
                    _log(f"espeak fallback failed ({err})")

        if not audio_path:
            raise RuntimeError(
                f"TTS synthesis failed for '{text}' across Edge TTS, gTTS, and espeak."
            )

        if self._terminate_flag:
            _log(f"Playback cancelled before start (_terminate_flag): '{text}'")
            return

        config = _load_config()
        vol = str(config.get("volume", 140))
        ao = config.get("audio_output", "pipewire,pulse")

        _log(f"Playing audio ({audio_path}): '{text}'")
        self._process = subprocess.Popen(
            [
                "mpv",
                "--no-terminal",
                "--no-config",
                "--load-scripts=no",
                "--force-window=no",
                "--audio-display=no",
                "--keep-open=no",
                "--input-media-keys=no",
                "--no-ytdl",
                f"--ao={ao}",
                f"--volume={vol}",
                "--volume-max=150",
                audio_path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._wait_for_termination(tag)
        _log(f"Finished playing audio: '{text}'")

    def _on_done(self, ret: Future, cb: OnDoneCallback) -> None:
        try:
            ret.result()
        except Exception as err:
            _log(f"Playback error in _on_done: {err}")
            tooltip(f"TTS error: {err}")
        cb()


def _register_player() -> None:
    if aqt.mw is not None and not any(
        isinstance(player, LinuxTTSPlayer) for player in av_player.players
    ):
        av_player.players.append(LinuxTTSPlayer(aqt.mw.taskman))
        _log("LinuxTTSPlayer registered in av_player.players")


gui_hooks.profile_did_open.append(_register_player)
_register_player()
