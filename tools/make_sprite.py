"""Crop, (optionally) de-checkerboard, and shrink one piece of art.

Usage:
  python make_sprite.py SRC OUT (--width W | --height H) [--key] [--figure N]

--key       remove a fake gray/white checkerboard background (for RGB images)
--figure N  the source holds several objects side by side; keep the Nth (0 = leftmost)
Sizes are the final file size in pixels (use 2x the CSS size for sharp Retina display).
"""
import argparse
from PIL import Image

def remove_checkerboard(im):
    """Fake transparency = light, colorless pixels. Clear them, but only where
    they connect to the image edge (flood fill), so light-gray parts INSIDE the
    art (stone steps, rocks) are kept."""
    im = im.convert('RGBA')
    px = im.load()
    w, h = im.size

    def is_bg(x, y):
        r, g, b, _ = px[x, y]
        return min(r, g, b) > 185 and max(r, g, b) - min(r, g, b) < 28

    stack = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    seen = set()
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h) or not is_bg(x, y):
            continue
        seen.add((x, y))
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    for x, y in seen:
        px[x, y] = (0, 0, 0, 0)

    # Background trapped inside the outline (e.g. between a porch post and a wall)
    # can't be reached from the edge. Clear any large pocket of pure checkerboard.
    visited = set(seen)
    for sy in range(h):
        for sx in range(w):
            if (sx, sy) in visited or px[sx, sy][3] == 0 or not is_bg(sx, sy):
                continue
            pocket, stack = [], [(sx, sy)]
            while stack:
                x, y = stack.pop()
                if (x, y) in visited or not (0 <= x < w and 0 <= y < h) or px[x, y][3] == 0 or not is_bg(x, y):
                    continue
                visited.add((x, y))
                pocket.append((x, y))
                stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
            # The checkerboard alternates two grays; real art pockets are one flat color
            grays = {round(px[x, y][0] / 12) for x, y in pocket}
            if len(pocket) > 400 and len(grays) >= 2:
                for x, y in pocket:
                    px[x, y] = (0, 0, 0, 0)
    return im

def figures(im, min_count=12):
    """Split side-by-side objects apart using empty columns between them."""
    a = im.getchannel('A').load()
    cols = [sum(1 for y in range(im.height) if a[x, y] > 10) >= min_count for x in range(im.width)]
    runs, start = [], None
    for x, on in enumerate(cols + [False]):
        if on and start is None:
            start = x
        elif not on and start is not None:
            if x - start > 40:
                runs.append((start, x))
            start = None
    return [im.crop((x0, 0, x1, im.height)) for x0, x1 in runs]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('out')
    size = ap.add_mutually_exclusive_group(required=True)
    size.add_argument('--width', type=int)
    size.add_argument('--height', type=int)
    ap.add_argument('--key', action='store_true')
    ap.add_argument('--figure', type=int)
    args = ap.parse_args()

    im = Image.open(args.src).convert('RGBA')
    if args.key:
        im = remove_checkerboard(im)
    if args.figure is not None:
        im = figures(im)[args.figure]

    # Tidy faint edge noise, then crop to the art
    alpha = im.getchannel('A').point(lambda v: 0 if v < 10 else v)
    im.putalpha(alpha)
    im = im.crop(alpha.getbbox())

    scale = args.width / im.width if args.width else args.height / im.height
    size = (round(im.width * scale), round(im.height * scale))
    # Premultiplied alpha avoids dark halos around the edges when shrinking
    small = im.convert('RGBa').resize(size, Image.LANCZOS).convert('RGBA')
    small.save(args.out, optimize=True)
    print(f'{args.out}: {small.width}x{small.height} (CSS {small.width / 2:g}x{small.height / 2:g})')

main()
