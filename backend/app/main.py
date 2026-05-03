import io
import base64
import uuid
import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image, ImageOps

from app.schemas import ConvertRequest, ConvertResponse
from app.processors.pixelate import calculate_grid_dimensions, pixelate
from app.processors.quantize import extract_colors, get_max_colors
from app.preprocess.denoise import denoise
from app.exporters.png_exporter import export_grid
from app.exporters.pdf_exporter import export_pdf

app = FastAPI(title="img2pixel", description="图片转像素图 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _load_image(data: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(data))
    transposed = ImageOps.exif_transpose(img)
    if transposed is not None:
        img = transposed
    return img.convert("RGB")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/convert", response_model=ConvertResponse)
async def convert(
    file: UploadFile = File(...),
    pixel_count: int = Form(600),
    color_mode: str = Form("balanced"),
    max_colors: int | None = Form(None),
    denoise_enabled: bool = Form(True),
    denoise_strength: float = Form(0.5),
):
    contents = await file.read()
    image = _load_image(contents)

    if denoise_enabled:
        image = denoise(image, denoise_strength)

    grid_w, grid_h = calculate_grid_dimensions(
        image.width, image.height, pixel_count
    )

    n_colors = get_max_colors(color_mode, max_colors)
    palette = extract_colors(image, n_colors)

    pixel_img = pixelate(image, grid_w, grid_h, palette)

    pixel_display = pixel_img.resize(
        (grid_w * 10, grid_h * 10), Image.NEAREST
    )
    grid_display = export_grid(pixel_img, cell_size=40)

    result_buf = io.BytesIO()
    pixel_display.save(result_buf, format="PNG")
    result_b64 = base64.b64encode(result_buf.getvalue()).decode()

    grid_buf = io.BytesIO()
    grid_display.save(grid_buf, format="PNG")
    grid_b64 = base64.b64encode(grid_buf.getvalue()).decode()

    palette_hex = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in palette]

    return ConvertResponse(
        grid_width=grid_w,
        grid_height=grid_h,
        total_pixels=grid_w * grid_h,
        palette=palette_hex,
        result_image=result_b64,
        grid_image=grid_b64,
    )


@app.post("/api/preview")
async def preview(
    file: UploadFile = File(...),
    denoise_enabled: bool = Form(True),
    denoise_strength: float = Form(0.5),
):
    contents = await file.read()
    image = _load_image(contents)

    if denoise_enabled:
        image = denoise(image, denoise_strength)

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return {"image": b64}


@app.post("/api/export")
async def export(
    file: UploadFile = File(...),
    export_format: str = Form("png"),
    pixel_count: int = Form(600),
    color_mode: str = Form("balanced"),
    max_colors: int | None = Form(None),
    denoise_enabled: bool = Form(True),
    denoise_strength: float = Form(0.5),
):
    contents = await file.read()
    image = _load_image(contents)

    if denoise_enabled:
        image = denoise(image, denoise_strength)

    grid_w, grid_h = calculate_grid_dimensions(
        image.width, image.height, pixel_count
    )
    n_colors = get_max_colors(color_mode, max_colors)
    palette = extract_colors(image, n_colors)
    pixel_img = pixelate(image, grid_w, grid_h, palette)

    if export_format == "pdf":
        pdf_bytes = export_pdf(pixel_img, palette)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="img2pixel_{grid_w}x{grid_h}.pdf"'
            },
        )
    else:
        grid_img = export_grid(pixel_img, cell_size=40)
        buf = io.BytesIO()
        grid_img.save(buf, format="PNG")
        return Response(
            content=buf.getvalue(),
            media_type="image/png",
            headers={
                "Content-Disposition": f'attachment; filename="img2pixel_{grid_w}x{grid_h}.png"'
            },
        )

