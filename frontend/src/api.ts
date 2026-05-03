import type { ConvertResponse, Params } from './types'

export async function convertImage(
  file: File,
  params: Params,
): Promise<ConvertResponse> {
  const form = new FormData()
  form.append('file', file)
  form.append('pixel_count', String(params.pixel_count))
  form.append('color_mode', params.color_mode)
  if (params.max_colors !== null) {
    form.append('max_colors', String(params.max_colors))
  }
  form.append('denoise_enabled', String(params.denoise))
  form.append('denoise_strength', String(params.denoise_strength))

  const res = await fetch(`/api/convert`, { method: 'POST', body: form })
  if (!res.ok) throw new Error('Conversion failed')
  return res.json()
}

export async function exportImage(
  file: File,
  params: Params,
  format: 'png' | 'pdf',
): Promise<Blob> {
  const form = new FormData()
  form.append('file', file)
  form.append('export_format', format)
  form.append('pixel_count', String(params.pixel_count))
  form.append('color_mode', params.color_mode)
  if (params.max_colors !== null) {
    form.append('max_colors', String(params.max_colors))
  }
  form.append('denoise_enabled', String(params.denoise))
  form.append('denoise_strength', String(params.denoise_strength))

  const res = await fetch(`/api/export`, { method: 'POST', body: form })
  if (!res.ok) throw new Error('Export failed')
  return res.blob()
}
