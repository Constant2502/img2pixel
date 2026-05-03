export interface ConvertResponse {
  grid_width: number
  grid_height: number
  total_pixels: number
  palette: string[]
  result_image: string
  grid_image: string
}

export interface Params {
  pixel_count: number
  color_mode: 'monochrome' | 'balanced' | 'realistic'
  max_colors: number | null
  denoise: boolean
  denoise_strength: number
  edge_preserve: boolean
  edge_strength: number
}
