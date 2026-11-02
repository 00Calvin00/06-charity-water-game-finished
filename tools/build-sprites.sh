#!/bin/bash
# Rebuild every game sprite in img/sprites/ from the original art in art-source/.
# Run from the project folder:  bash tools/build-sprites.sh
# Needs Python with Pillow (see tools/README.md).
#
# Sizes are the FILE size: 2x the size shown in the game (see styles.css),
# so sprites stay sharp on high-resolution screens.
set -e

PYTHON="${PYTHON:-python3}"
SRC=art-source
OUT=img/sprites

# Player: idle + 3 walk frames in one sheet, 80px tall (shown 40px tall)
"$PYTHON" tools/make_player_sheet.py $SRC/player-idle.png $SRC/player-walk.png $OUT/player-sheet.png 80

# Map objects
"$PYTHON" tools/make_sprite.py $SRC/house.png      $OUT/house.png      --width 104 --key   # fake checkerboard background
"$PYTHON" tools/make_sprite.py $SRC/tree.png       $OUT/tree.png       --height 96
"$PYTHON" tools/make_sprite.py $SRC/pump.png       $OUT/pump.png       --height 134
"$PYTHON" tools/make_sprite.py $SRC/pond-clean.png $OUT/pond-clean.png --width 276

# This file holds two ponds side by side: dried (left) and dirty (right)
"$PYTHON" tools/make_sprite.py $SRC/ponds-dried-and-dirty.png $OUT/pond-dried.png --width 276 --figure 0
"$PYTHON" tools/make_sprite.py $SRC/ponds-dried-and-dirty.png $OUT/pond-dirty.png --width 276 --figure 1
