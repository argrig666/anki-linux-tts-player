.PHONY: addon clean

addon:
	python3 package.py

clean:
	rm -f linux_tts_player.ankiaddon
