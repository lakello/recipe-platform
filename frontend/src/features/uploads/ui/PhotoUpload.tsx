import { useRef } from 'react'
import { Button } from '@/shared/ui/Button'

interface PhotoUploadProps {
  currentUrl?: string
  onUpload: (file: File) => void
  onRemove?: () => void
  isPending: boolean
  error: string | null
  label?: string
  shape?: 'square' | 'circle'
}

export function PhotoUpload({
  currentUrl,
  onUpload,
  onRemove,
  isPending,
  error,
  label = 'Загрузить фото',
  shape = 'square',
}: PhotoUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) onUpload(file)
    e.target.value = ''
  }

  const shapeClass = shape === 'circle' ? 'rounded-full' : 'rounded-xl'

  return (
    <div className="flex flex-col gap-2">
      {currentUrl && (
        <div className={`relative w-32 h-32 overflow-hidden ${shapeClass} bg-gray-100`}>
          <img src={currentUrl} alt="фото" className="w-full h-full object-cover" />
        </div>
      )}

      {!currentUrl && (
        <div
          className={`w-32 h-32 ${shapeClass} bg-gray-100 border-2 border-dashed border-gray-300 flex items-center justify-center cursor-pointer hover:bg-gray-50`}
          onClick={() => inputRef.current?.click()}
        >
          <span className="text-gray-400 text-sm text-center px-2">
            {isPending ? 'Загрузка...' : 'Нажмите для выбора'}
          </span>
        </div>
      )}

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={handleChange}
      />

      <div className="flex gap-2">
        <Button
          variant="secondary"
          loading={isPending}
          onClick={() => inputRef.current?.click()}
        >
          {currentUrl ? 'Заменить' : label}
        </Button>
        {currentUrl && onRemove && (
          <Button variant="danger" loading={isPending} onClick={onRemove}>
            Удалить
          </Button>
        )}
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  )
}
