import numpy as np
from sklearn.cluster import KMeans
from PIL import Image


def extract_colors(image: Image.Image, n_colors: int) -> list[tuple[int, int, int]]:
    img_array = np.array(image.convert("RGB"))
    h, w, _ = img_array.shape
    pixels = img_array.reshape(-1, 3)

    if n_colors == 1:
        avg = pixels.mean(axis=0)
        return [(int(avg[0]), int(avg[1]), int(avg[2]))]

    n_clusters = min(n_colors, len(pixels))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)
    result = [(int(r), int(g), int(b)) for r, g, b in colors]
    result.sort(key=lambda c: _color_luminance(c), reverse=True)
    return result


def _color_luminance(color: tuple[int, int, int]) -> float:
    return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]


def get_max_colors(mode: str, user_max: int | None) -> int:
    if user_max is not None:
        return max(1, user_max)
    defaults = {"monochrome": 1, "balanced": 6, "realistic": 20}
    return defaults.get(mode, 6)
