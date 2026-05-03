import math
import numpy as np
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


def _luminance(rgb: np.ndarray) -> np.ndarray:
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def _sample_cell(arr: np.ndarray) -> np.ndarray:
    avg = arr.mean(axis=(0, 1))
    lum = _luminance(arr)
    lo, hi = lum.min(), lum.max()
    spread = hi - lo
    if spread > 25 and lo < 100:
        pct = 10 if spread > 60 else 20
        thresh = np.percentile(lum, pct)
        dark = arr[lum <= thresh]
        if len(dark) >= 3:
            return dark.mean(axis=0)
    return avg


def _enforce_symmetry(grid: np.ndarray) -> np.ndarray:
    h, w = grid.shape[:2]
    mid = w // 2
    for y in range(h):
        for x in range(mid):
            rx = w - 1 - x
            dl = _luminance(grid[y, x].reshape(1, 1, 3)).item()
            dr = _luminance(grid[y, rx].reshape(1, 1, 3)).item()
            if dl < dr:
                grid[y, rx] = grid[y, x]
            else:
                grid[y, x] = grid[y, rx]
    return grid


def pixelate(
    image: Image.Image,
    grid_w: int,
    grid_h: int,
    palette: list[tuple[int, int, int]],
    symmetry: bool = True,
) -> Image.Image:
    arr = np.array(image.convert("RGB"))
    h, w = arr.shape[:2]
    out = np.zeros((grid_h, grid_w, 3), dtype=np.uint8)

    for gy in range(grid_h):
        y0 = int(gy * h / grid_h)
        y1 = int((gy + 1) * h / grid_h)
        for gx in range(grid_w):
            x0 = int(gx * w / grid_w)
            x1 = int((gx + 1) * w / grid_w)
            cell = arr[y0:y1, x0:x1]
            color = _sample_cell(cell)
            out[gy, gx] = _closest_color(color, palette)

    if symmetry and grid_w > 3:
        out = _enforce_symmetry(out)

    return Image.fromarray(out)


def _closest_color(
    color: np.ndarray | tuple[int, int, int],
    palette: list[tuple[int, int, int]],
) -> tuple[int, int, int]:
    min_dist = float("inf")
    best = palette[0]
    for pc in palette:
        dr = float(color[0]) - pc[0]
        dg = float(color[1]) - pc[1]
        db = float(color[2]) - pc[2]
        dist = dr * dr + dg * dg + db * db
        if dist < min_dist:
            min_dist = dist
            best = pc
    return best
