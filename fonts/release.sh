#!/bin/sh

# curl -L -o noto-emoji/NotoColorEmoji.ttf    https://raw.githubusercontent.com/googlefonts/noto-emoji/main/fonts/NotoColorEmoji.ttf
# curl -L -o noto-emoji/NotoEmoji-Regular.ttf https://raw.githubusercontent.com/googlefonts/noto-emoji/main/fonts/NotoEmoji-Regular.ttf
# curl -L -o twemoji-colr/TwemojiMozilla.ttf  https://github.com/mozilla/twemoji-colr/releases/download/v0.7.0/Twemoji.Mozilla.ttf

rm */.DS_Store
zip -r -9 noto-emoji.zip   noto-emoji
zip -r -9 twemoji-colr.zip twemoji-colr
mv *.zip ../release
