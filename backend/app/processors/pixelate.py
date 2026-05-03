import math
from PIL import Image


def calculate_grid_dimensions(
    img_width: int, img_height: int, target_pixels: int
) -> tuple[int, int]:
    ratio = img_width / img_height
    grid_w = math.sqrt(target_pixels * ratio)
    grid_h = target_pixels / grid_w

    w1, h1 = int(grid_w), int(round(grid_h))
    w2, h2 = int(round(grid_w)), int(grid_h)

    candidates = [(w1, h1), (w2, h1), (w1, h2), (w2, h2)]
    best = min(
        candidates,
        key=lambda wh: (
            abs(wh[0] * wh[1] - target_pixels),
            abs(wh[0] / wh[1] - ratio),
        ),
    )

    best = (max(1, best[0]), max(1, best[1]))
    return best


def pixelate(
    image: Image.Image,
    grid_w: int,
    grid_h: int,
    palette: list[tuple[int, int, int]],
) -> Image.Image:
    small = image.resize((grid_w, grid_h), Image.LANCZOS)
    pixels = small.load()
    for y in range(grid_h):
        for x in range(grid_w):
            r, g, b = pixels[x, y][:3]
            pixels[x, y] = _closest_color((r, g, b), palette)
    return small


def _closest_color(
    color: tuple[int, int, int],
    palette: list[tuple[int, int, int]],
) -> tuple[int, int, int]:
    min_dist = float("inf")
    best = palette[0]
    for pc in palette:
        dr = color[0] - pc[0]
        dg = color[1] - pc[1]
        db = color[2] - pc[2]
        dist = dr * dr + dg * dg + db * db
        if dist < min_dist:
            min_dist = dist
            best = pc
    return best
