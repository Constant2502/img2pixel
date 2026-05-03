import io
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing, Rect, String


def export_pdf(
    pixel_image: Image.Image,
    palette: list[tuple[int, int, int]],
    output_path: str | None = None,
) -> bytes:
    grid_w, grid_h = pixel_image.size
    buf = io.BytesIO()

    page_w, page_h = landscape(A4)
    margin = 20 * mm
    draw_w = page_w - 2 * margin
    draw_h = page_h - 2 * margin
    cell_size = min(draw_w / grid_w, draw_h / grid_h)

    c = canvas.Canvas(buf, pagesize=landscape(A4))
    c.setTitle("img2pixel - 拼豆像素图")

    pixels = pixel_image.load()

    y_offset = page_h - margin
    for y in range(grid_h):
        for x in range(grid_w):
            color = pixels[x, y]
            if isinstance(color, tuple) and len(color) >= 3:
                r, g, b = color[:3]
            else:
                r = g = b = color
            x0 = margin + x * cell_size
            y0 = y_offset - (y + 1) * cell_size
            c.setFillColorRGB(r / 255, g / 255, b / 255)
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.setLineWidth(0.5)
            c.rect(x0, y0, cell_size, cell_size, fill=1, stroke=1)

    c.showPage()
    c.save()

    buf.seek(0)
    return buf.getvalue()
