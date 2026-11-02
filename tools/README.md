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
