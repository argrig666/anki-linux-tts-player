.PHONY: addon
addon:
	rm -f linux_tts_player.ankiaddon
	zip -r linux_tts_player.ankiaddon \
		__init__.py config.json config.md manifest.json vendor \
		-x '*/__pycache__/*' '*.pyc'
