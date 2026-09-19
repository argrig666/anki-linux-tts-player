# Configuration Guide

### `default_voices`
Map Anki language codes (e.g., `it_IT`, `fr_FR`, `en_US`) to your preferred Microsoft Azure / Edge Neural voice.
When a card template specifies a general language tag without a voice parameter (e.g. `{{tts it_IT:Field}}`), the voice specified here will be prioritized.

Available popular voices include:
- **Italian (`it_IT`)**: `it-IT-ElsaNeural` (Female), `it-IT-DiegoNeural` (Male), `it-IT-IsabellaNeural` (Female), `it-IT-GiuseppeMultilingualNeural` (Male)
- **French (`fr_FR`)**: `fr-FR-VivienneMultilingualNeural` (Female), `fr-FR-DeniseNeural` (Female), `fr-FR-HenriNeural` (Male), `fr-FR-EloiseNeural` (Female), `fr-FR-RemyMultilingualNeural` (Male)
- **French Canada (`fr_CA`)**: `fr-CA-SylvieNeural` (Female), `fr-CA-JeanNeural` (Male), `fr-CA-AntoineNeural` (Male)
- **English US (`en_US`)**: `en-US-JennyNeural` (Female), `en-US-GuyNeural` (Male), `en-US-AriaNeural` (Female)
- **English UK (`en_GB`)**: `en-GB-SoniaNeural` (Female), `en-GB-RyanNeural` (Male)
- **German (`de_DE`)**: `de-DE-KatjaNeural` (Female), `de-DE-ConradNeural` (Male)
- **Spanish (`es_ES`)**: `es-ES-ElviraNeural` (Female), `es-ES-AlvaroNeural` (Male)
- **Russian (`ru_RU`)**: `ru-RU-SvetlanaNeural` (Female), `ru-RU-DmitryNeural` (Male)
- **Japanese (`ja_JP`)**: `ja-JP-NanamiNeural` (Female), `ja-JP-KeitaNeural` (Male)

### `volume`
Software playback volume in percent (default: `140`). Neural TTS voices can be soft relative to desktop media; values between `100` and `150` ensure speech is crisp and easily audible over laptop speakers.

### `audio_output`
Audio driver used by mpv (default: `"pipewire,pulse"`).

### `debug_log`
Set to `true` to record timestamped voice matching and playback traces to `user_files/debug.log`.
