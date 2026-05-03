import { useState, useCallback } from 'react'
import type { Params, ConvertResponse } from './types'
import { convertImage, exportImage } from './api'
import ImageUploader from './components/ImageUploader'
import ParameterPanel from './components/ParameterPanel'
import PreviewPanel from './components/PreviewPanel'
import './App.css'

const DEFAULT_PARAMS: Params = {
  pixel_count: 600,
  color_mode: 'balanced',
  max_colors: 6,
  denoise: true,
  denoise_strength: 0.5,
}

export default function App() {
  const [file, setFile] = useState<File | null>(null)
  const [params, setParams] = useState<Params>(DEFAULT_PARAMS)
  const [result, setResult] = useState<ConvertResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFile = useCallback((f: File) => {
    setFile(f)
    setResult(null)
    setError(null)
  }, [])

  const handleConvert = useCallback(async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const res = await convertImage(file, params)
      setResult(res)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }, [file, params])

  const handleExport = useCallback(
    async (format: 'png' | 'pdf') => {
      if (!file) return
      try {
        const blob = await exportImage(file, params, format)
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `img2pixel_${result?.grid_width}x${result?.grid_height}.${format}`
        a.click()
        URL.revokeObjectURL(url)
      } catch (e) {
        setError(String(e))
      }
    },
    [file, params, result],
  )

  return (
    <div className="app">
      <header>
        <h1>img2pixel</h1>
        <p>图片转像素图 — 拼豆必备</p>
      </header>

      <main>
        <section className="upload-section">
          <ImageUploader onFileSelect={handleFile} file={file} />
        </section>

        <section className="params-section">
          <ParameterPanel params={params} onChange={setParams} />
        </section>

        <section className="actions">
          <button onClick={handleConvert} disabled={!file || loading}>
            {loading ? '处理中...' : '转换'}
          </button>
          {result && (
            <>
              <button onClick={() => handleExport('png')}>导出 PNG</button>
              <button onClick={() => handleExport('pdf')}>导出 PDF</button>
            </>
          )}
        </section>

        <section className="preview-section">
          <PreviewPanel
            result={result}
            originalUrl={file ? URL.createObjectURL(file) : null}
            loading={loading}
            error={error}
          />
        </section>
      </main>
    </div>
  )
}
