import numpy as np
from sklearn.cluster import KMeans
from sklearn.utils import shuffle
from PIL import Image


def _kmeans_colors(pixels: np.ndarray, n: int) -> np.ndarray:
    n = min(n, len(pixels))
    if n <= 0:
        return np.empty((0, 3), dtype=int)
    sampled = shuffle(pixels, n_samples=min(30000, len(pixels)), random_state=42)
    kmeans = KMeans(n_clusters=min(n, len(sampled)), random_state=42, n_init="auto")
    kmeans.fit(sampled)
    return kmeans.cluster_centers_.astype(int)


def _deduplicate(colors: np.ndarray, n_target: int, threshold: float = 30) -> np.ndarray:
    if len(colors) <= n_target:
        return colors

    merged = list(colors)
    while len(merged) > n_target:
        n = len(merged)
        min_d = float("inf")
        merge_pair = (0, 1)
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(merged[i] - merged[j])
                if d < min_d:
                    min_d = d
                    merge_pair = (i, j)
        if min_d > threshold:
            break
        i, j = merge_pair
        avg = ((merged[i] + merged[j]) / 2).astype(int)
        merged.pop(j)
        merged.pop(i)
        merged.append(avg)

    return np.array(merged)


def extract_colors(
    image: Image.Image,
    n_colors: int,
) -> list[tuple[int, int, int]]:
    img_array = np.array(image.convert("RGB"))
    pixels = img_array.reshape(-1, 3)

    if n_colors == 1:
        avg = pixels.mean(axis=0)
        return [(int(avg[0]), int(avg[1]), int(avg[2]))]

    candidates = _kmeans_colors(pixels, n_colors * 2)
    all_colors = _deduplicate(candidates, n_colors)

    while len(all_colors) < n_colors:
        all_colors = np.vstack([all_colors, all_colors[:1]])

    result = [(int(r), int(g), int(b)) for r, g, b in all_colors[:n_colors]]
    result.sort(key=lambda c: _color_luminance(c), reverse=True)
    return result


def _color_luminance(color: tuple[int, int, int]) -> float:
    return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]


def get_max_colors(mode: str, user_max: int | None) -> int:
    if user_max is not None:
        return max(1, user_max)
    defaults = {"monochrome": 1, "balanced": 6, "realistic": 20}
    return defaults.get(mode, 6)
