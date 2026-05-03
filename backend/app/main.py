import io
import base64
import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image, ImageOps

from app.schemas import ConvertRequest, ConvertResponse
import numpy as np
from app.processors.pixelate import calculate_grid_dimensions, pixelate
from app.processors.quantize import extract_colors, get_max_colors
from app.processors.edge_preserve import (
    compute_edge_map,
    downscale_edge_map,
    generate_outline_mask,
    darken_outline,
)
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


def _process_image(
    image: Image.Image,
    pixel_count: int,
    color_mode: str,
    max_colors: int | None,
    edge_preserve: bool,
    edge_strength: float,
) -> tuple[Image.Image, int, int, list[tuple[int, int, int]], list[str]]:
    grid_w, grid_h = calculate_grid_dimensions(
        image.width, image.height, pixel_count
    )

    edge_map = compute_edge_map(image) if (edge_preserve and edge_strength > 0) else None

    n_colors = get_max_colors(color_mode, max_colors)
    palette_raw = extract_colors(image, n_colors)

    pixel_img = pixelate(image, grid_w, grid_h, palette_raw)

    if edge_map is not None:
        edge_grid = downscale_edge_map(edge_map, grid_w, grid_h)
        mask = generate_outline_mask(edge_grid, threshold_percentile=80)
        arr = np.array(pixel_img.convert("RGB"))
        arr = darken_outline(arr, mask, strength=edge_strength)
        pixel_img = Image.fromarray(arr)

    palette_hex = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in palette_raw]
    return pixel_img, grid_w, grid_h, palette_raw, palette_hex


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
    edge_preserve: bool = Form(True),
    edge_strength: float = Form(0.35),
):
    contents = await file.read()
    image = _load_image(contents)

    if denoise_enabled:
        image = denoise(image, denoise_strength)

    pixel_img, grid_w, grid_h, _, palette_hex = _process_image(
        image, pixel_count, color_mode, max_colors, edge_preserve, edge_strength
    )

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
    edge_preserve: bool = Form(True),
    edge_strength: float = Form(0.35),
):
    contents = await file.read()
    image = _load_image(contents)

    if denoise_enabled:
        image = denoise(image, denoise_strength)

    pixel_img, grid_w, grid_h, palette_raw, palette_hex = _process_image(
        image, pixel_count, color_mode, max_colors, edge_preserve, edge_strength
    )

    if export_format == "pdf":
        pdf_bytes = export_pdf(pixel_img, palette_raw)
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

