"""Make a plain, speckled ground tile from the colors of a pixel-art sample.

The sample's shapes (dunes, cracks...) are NOT kept, only its colors. Shapes are what
make a repeating tile look like a repeating pattern; scattered specks blend together.

Usage:
  python make_ground_tile.py SRC OUT --grid 32 --size 64 --zoom 6 [--trim 10]
                             [--specks 0.25] [--soften 0.5] [--seed 7]

--grid    how many art pixels across the sample is (used to read its colors cleanly)
--size    how many art pixels across the new tile is (bigger = repeats less often)
--zoom    how many file pixels each art pixel becomes (hard edges, no blur).
          Use 2x the CSS size: zoom 6 = 3 CSS pixels per art pixel.
--trim    pixels to cut off each edge of the sample first (e.g. a colored frame)
--specks  how many pixels are a random sand color instead of the plain base color (0 to 1)
--soften  fade the whole tile toward the average color: 0 = no fade, 1 = one flat color
--seed    the same seed always makes the same tile
"""
import argparse
import random
from PIL import Image

def sample_colors(im, n):
    """Read the sample at its real size: one color per art pixel, taken from
    the middle of each block (the edges are blurry in a JPEG)."""
    cell = im.width / n
    px = im.load()
    colors = []
    for gy in range(n):
        for gx in range(n):
            x0, y0 = int((gx + 0.3) * cell), int((gy + 0.3) * cell)
            x1, y1 = int((gx + 0.7) * cell), int((gy + 0.7) * cell)
            block = sorted(px[x, y] for x in range(x0, x1) for y in range(y0, y1))
            colors.append(block[len(block) // 2])
    return colors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('out')
    ap.add_argument('--grid', type=int, required=True)
    ap.add_argument('--size', type=int, required=True)
    ap.add_argument('--zoom', type=int, required=True)
    ap.add_argument('--trim', type=int, default=0)
    ap.add_argument('--specks', type=float, default=0.25)
    ap.add_argument('--soften', type=float, default=0.5)
    ap.add_argument('--seed', type=int, default=7)
    args = ap.parse_args()

    im = Image.open(args.src).convert('RGB')
    t = args.trim
    colors = sample_colors(im.crop((t, t, im.width - t, im.height - t)), args.grid)

    # The base color: the sample's color closest to its average
    average = tuple(sum(c[i] for c in colors) // len(colors) for i in range(3))
    base = min(colors, key=lambda c: sum((a - b) ** 2 for a, b in zip(c, average)))

    # Mostly base color, with a few specks picked from the sample's colors.
    # Random specks have no shapes, so the tile has no edges to line up: it's seamless.
    rng = random.Random(args.seed)
    n = args.size
    tile = Image.new('RGB', (n, n))
    for y in range(n):
        for x in range(n):
            tile.putpixel((x, y), rng.choice(colors) if rng.random() < args.specks else base)

    tile = Image.blend(tile, Image.new('RGB', tile.size, average), args.soften)
    big = tile.resize((n * args.zoom, n * args.zoom), Image.NEAREST)
    big.save(args.out, optimize=True)
    print(f'{args.out}: {big.width}x{big.height} (CSS {big.width / 2:g}x{big.height / 2:g})')

main()
