import { useState } from 'react'
import type { Params } from '../types'

const COLOR_MODES = [
  { value: 'monochrome', label: '单色' },
  { value: 'balanced', label: '均衡' },
  { value: 'realistic', label: '写实' },
] as const

interface Props {
  params: Params
  onChange: (p: Params) => void
}

export default function ParameterPanel({ params, onChange }: Props) {
  const set = (patch: Partial<Params>) => onChange({ ...params, ...patch })
  const [pixelInput, setPixelInput] = useState(String(params.pixel_count))

  const modeDefaultColors: Record<string, number | null> = {
    monochrome: null,
    balanced: 6,
    realistic: 20,
  }

  return (
    <div className="params">
      <label>
        像素数量
        <input
          type="number"
          min={16}
          max={10000}
          value={pixelInput}
          onChange={(e) => setPixelInput(e.target.value)}
          onBlur={() => {
            const v = Math.max(16, Math.min(10000, Number(pixelInput) || 600))
            setPixelInput(String(v))
            set({ pixel_count: v })
          }}
        />
      </label>

      <label>
        颜色模式
        <select
          value={params.color_mode}
          onChange={(e) => {
            const mode = e.target.value as Params['color_mode']
            set({ color_mode: mode, max_colors: modeDefaultColors[mode] })
          }}
        >
          {COLOR_MODES.map((m) => (
            <option key={m.value} value={m.value}>{m.label}</option>
          ))}
        </select>
      </label>

      <label>
        最大颜色数
        <input
          type="number"
          min={1}
          max={256}
          value={params.max_colors ?? ''}
          placeholder="自动"
          disabled={params.color_mode === 'monochrome'}
          onChange={(e) =>
            set({ max_colors: e.target.value ? Number(e.target.value) : null })
          }
        />
      </label>

      <label className="checkbox-label">
        <input
          type="checkbox"
          checked={params.denoise}
          onChange={(e) => set({ denoise: e.target.checked })}
        />
        自动去噪
      </label>

      {params.denoise && (
        <label>
          去噪强度
          <input
            type="range"
            min={0}
            max={1}
            step={0.1}
            value={params.denoise_strength}
            onChange={(e) => set({ denoise_strength: Number(e.target.value) })}
          />
          <span className="range-value">{params.denoise_strength.toFixed(1)}</span>
        </label>
      )}
    </div>
  )
}
