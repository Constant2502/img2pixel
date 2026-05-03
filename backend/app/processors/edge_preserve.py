import numpy as np
from PIL import Image, ImageFilter


def compute_edge_map(image: Image.Image) -> np.ndarray:
    gray = image.convert("L")
    arr = np.array(gray, dtype=np.float32)

    gx = np.zeros_like(arr)
    gy = np.zeros_like(arr)
    gx[:, :-1] = np.abs(arr[:, 1:] - arr[:, :-1])
    gy[:-1, :] = np.abs(arr[1:, :] - arr[:-1, :])

    magnitude = np.sqrt(gx ** 2 + gy ** 2)
    magnitude = (magnitude / magnitude.max() * 255).astype(np.uint8)
    return magnitude


def downscale_edge_map(
    edge_map: np.ndarray, grid_w: int, grid_h: int
) -> np.ndarray:
    h, w = edge_map.shape
    edge_img = Image.fromarray(edge_map)
    edge_small = edge_img.resize((grid_w, grid_h), Image.LANCZOS)
    return np.array(edge_small, dtype=np.float32)


def generate_outline_mask(
    edge_grid: np.ndarray, threshold_percentile: float = 85
) -> np.ndarray:
    if edge_grid.max() == edge_grid.min():
        return np.zeros_like(edge_grid, dtype=bool)
    threshold = np.percentile(edge_grid, threshold_percentile)
    return edge_grid >= threshold


def darken_outline(
    pixel_arr: np.ndarray, mask: np.ndarray, strength: float = 0.4
) -> np.ndarray:
    result = pixel_arr.copy().astype(np.float32)
    for c in range(3):
        result[:, :, c] = np.where(
            mask,
            result[:, :, c] * (1 - strength),
            result[:, :, c],
        )
    return np.clip(result, 0, 255).astype(np.uint8)
