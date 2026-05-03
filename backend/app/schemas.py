from pydantic import BaseModel
from typing import Optional


class ConvertRequest(BaseModel):
    pixel_count: int = 600
    color_mode: str = "balanced"  # monochrome | balanced | realistic
    max_colors: Optional[int] = None
    denoise: bool = True
    denoise_strength: float = 0.5


class ConvertResponse(BaseModel):
    grid_width: int
    grid_height: int
    total_pixels: int
    palette: list[str]
    result_image: str  # base64 PNG
    grid_image: str    # base64 PNG with grid lines


class ExportRequest(BaseModel):
    format: str = "png"  # png | pdf
    pixel_count: int = 600
    color_mode: str = "balanced"
    max_colors: Optional[int] = None
    denoise: bool = True
    denoise_strength: float = 0.5
