"""Turn the idle + walk art into one transparent sprite sheet.

Usage: python make_player_sheet.py idle.png walk.png out.png CELL_HEIGHT
Frames in the sheet, left to right: idle, walk1, walk2, walk3.
Every frame: feet on the bottom edge, helmet centered horizontally
(so flipping with scaleX(-1) doesn't make the character jump).
"""
import sys
from PIL import Image

def remove_background(im):
    """Fake checkerboard = light, colorless pixels. Make them transparent."""
    im = im.convert('RGBA')
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, _ = px[x, y]
            if min(r, g, b) > 185 and max(r, g, b) - min(r, g, b) < 28:
                px[x, y] = (0, 0, 0, 0)
    return im

def solid_columns(im, min_count=12):
    """Which columns contain real character pixels (ignores stray specks)."""
    w, h = im.size
    a = im.getchannel('A').load()
    return [sum(1 for y in range(h) if a[x, y] > 0) >= min_count for x in range(w)]

def split_figures(im):
    """Split an image into one crop per figure, using empty columns as gaps."""
    cols = solid_columns(im)
    runs, start = [], None
    for x, on in enumerate(cols + [False]):
        if on and start is None:
            start = x
        elif not on and start is not None:
            if x - start > 40:
                runs.append((start, x))
            start = None
    figures = []
    for x0, x1 in runs:
        part = im.crop((x0, 0, x1, im.height))
        figures.append(part.crop(part.getbbox()))
    return figures

def helmet_center_x(fig):
    """Average x of the yellow helmet pixels: a steady anchor across frames."""
    px = fig.load()
    xs = [x for y in range(fig.height // 3) for x in range(fig.width)
          if px[x, y][3] > 0 and px[x, y][0] > 200 and px[x, y][1] > 140 and px[x, y][2] < 110]
    return sum(xs) / len(xs)

def shrink(fig, scale):
    size = (max(1, round(fig.width * scale)), max(1, round(fig.height * scale)))
    # Premultiplied alpha avoids gray halos around the edges when shrinking
    return fig.convert('RGBa').resize(size, Image.LANCZOS).convert('RGBA')

def main():
    idle_path, walk_path, out_path, cell_h = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    idle = split_figures(remove_background(Image.open(idle_path)))
    walks = split_figures(remove_background(Image.open(walk_path)))
    assert len(idle) == 1 and len(walks) == 3, (len(idle), len(walks))

    # Idle is scaled to fill the cell height; all walk frames share one scale
    # (based on the tallest) so they don't grow/shrink between frames.
    walk_scale = cell_h / max(f.height for f in walks)
    frames = [(idle[0], cell_h / idle[0].height)] + [(f, walk_scale) for f in walks]

    placed = []
    for fig, scale in frames:
        small = shrink(fig, scale)
        anchor = helmet_center_x(fig) * scale
        placed.append((small, anchor))

    # Cell wide enough for the farthest pixel on either side of the anchor
    half = max(max(a, s.width - a) for s, a in placed)
    cell_w = int(2 * half + 0.999)
    cell_w += cell_w % 2

    sheet = Image.new('RGBA', (cell_w * len(placed), cell_h), (0, 0, 0, 0))
    for i, (small, anchor) in enumerate(placed):
        x = i * cell_w + round(cell_w / 2 - anchor)
        sheet.alpha_composite(small, (x, cell_h - small.height))
    sheet.save(out_path, optimize=True)
    print(f'{out_path}: {sheet.width}x{sheet.height}, cell {cell_w}x{cell_h}, {len(placed)} frames')

main()
