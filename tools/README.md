# Art tools

These scripts are not part of the game. They turn the big original art in `art-source/`
into the small, transparent sprites the game uses in `img/sprites/`.

## Setup (once)

```bash
python3 -m venv .venv
.venv/bin/pip install pillow
```

## Rebuild all sprites

```bash
PYTHON=.venv/bin/python bash tools/build-sprites.sh
```

## Adding new art

1. Put the original image in `art-source/` (a short name with no spaces, like `rock.png`).
2. Add a line for it to `tools/build-sprites.sh`. Pick a size 2x what it should look like in the game:
   - `--width W` or `--height H`: final file size in pixels
   - `--key`: the image has a fake gray/white checkerboard instead of real transparency
   - `--figure N`: the image has several objects side by side; keep the Nth one (0 = leftmost)
3. Run the build, then add a CSS class for it in `styles.css` (see `.house` or `.tree`).

## Background music

`audio/music-loop.m4a` is one track (1:25.913 - 2:55.540) from AlkaKrab's
"Free 12 Tracks Pixel RPG Game Music Pack". The full pack isn't kept in the repo.

It was cut sample-accurately: the whole MP3 was decoded to WAV first
(`afconvert -f WAVE -d LEI16 pack.mp3 pack.wav`), the track was cut out of the WAV
with a 5 ms fade at each end, and the cut was encoded with
`afconvert -f m4af -d aac -b 128000 cut.wav audio/music-loop.m4a`.
Don't cut straight from the MP3 with a start time (for example with `avconvert --start`):
seeking in this MP3 lands a few seconds off, which puts the end of the previous track
and a silent gap at the start of the loop.
