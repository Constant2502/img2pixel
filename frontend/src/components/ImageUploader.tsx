import { useCallback, useRef, useState } from 'react'

interface Props {
  onFileSelect: (file: File) => void
  file: File | null
}

export default function ImageUploader({ onFileSelect, file }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)

  const handleFile = useCallback(
    (f: File) => {
      if (f.type.startsWith('image/')) onFileSelect(f)
    },
    [onFileSelect],
  )

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragOver(false)
      const f = e.dataTransfer.files[0]
      if (f) handleFile(f)
    },
    [handleFile],
  )

  const onChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const f = e.target.files?.[0]
      if (f) handleFile(f)
    },
    [handleFile],
  )

  return (
    <div
      className={`uploader ${dragOver ? 'drag-over' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={onDrop}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        hidden
        onChange={onChange}
      />
      {file ? (
        <img
          src={URL.createObjectURL(file)}
          alt="preview"
          className="upload-preview"
        />
      ) : (
        <p>点击或拖拽上传图片</p>
      )}
    </div>
  )
}
