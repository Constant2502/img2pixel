from PIL import Image, ImageFilter


def denoise(image: Image.Image, strength: float = 0.5) -> Image.Image:
    if strength <= 0:
        return image
    radius = max(1, int(strength * 3))
    return image.filter(ImageFilter.MedianFilter(size=radius))
