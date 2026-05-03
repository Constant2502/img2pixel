import type { ConvertResponse } from '../types'

interface Props {
  result: ConvertResponse | null
  originalUrl: string | null
  loading: boolean
  error: string | null
}

export default function PreviewPanel({ result, originalUrl, loading, error }: Props) {
  return (
    <div className="preview">
      {error && <div className="error">{error}</div>}

      <div className="preview-images">
        <div className="preview-col">
          <h3>原始图片</h3>
          {originalUrl ? (
            <img src={originalUrl} alt="original" />
          ) : (
            <div className="placeholder">请上传图片</div>
          )}
        </div>

        <div className="preview-col">
          <h3>转换结果</h3>
          {loading ? (
            <div className="placeholder">处理中...</div>
          ) : result ? (
            <>
              <img
                src={`data:image/png;base64,${result.result_image}`}
                alt="result"
              />
              <div className="result-info">
                <span>{result.grid_width}×{result.grid_height}</span>
                <span>共 {result.total_pixels} 像素</span>
                <span>调色板：</span>
                <div className="palette">
                  {result.palette.map((c, i) => (
                    <span
                      key={i}
                      className="swatch"
                      style={{ background: c }}
                      title={c}
                    />
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="placeholder">等待转换</div>
          )}
        </div>
      </div>

      {result && (
        <img
          src={`data:image/png;base64,${result.grid_image}`}
          alt="grid"
          className="grid-image"
        />
      )}
    </div>
  )
}
