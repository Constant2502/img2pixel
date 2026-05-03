from PIL import Image, ImageDraw


def export_grid(pixel_image: Image.Image, cell_size: int = 40) -> Image.Image:
    grid_w, grid_h = pixel_image.size
    out_w = grid_w * cell_size
    out_h = grid_h * cell_size
    out = Image.new("RGB", (out_w, out_h), (255, 255, 255))
    draw = ImageDraw.Draw(out)

    pixels = pixel_image.load()
    for y in range(grid_h):
        for x in range(grid_w):
            color = pixels[x, y]
            if isinstance(color, tuple) and len(color) >= 3:
                r, g, b = color[:3]
            else:
                r = g = b = color
            x0 = x * cell_size
            y0 = y * cell_size
            x1 = x0 + cell_size
            y1 = y0 + cell_size
            draw.rectangle([x0, y0, x1, y1], fill=(r, g, b))
            draw.rectangle([x0, y0, x1, y1], outline=(200, 200, 200), width=1)

    return out
