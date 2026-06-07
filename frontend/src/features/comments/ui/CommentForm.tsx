import { useState } from 'react'
import { Button } from '@/shared/ui/Button'

interface CommentFormProps {
  onSubmit: (body: string) => void
  onCancel?: () => void
  isPending: boolean
  placeholder?: string
  defaultValue?: string
  submitLabel?: string
}

export function CommentForm({
  onSubmit,
  onCancel,
  isPending,
  placeholder = 'Напишите комментарий...',
  defaultValue = '',
  submitLabel = 'Отправить',
}: CommentFormProps) {
  const [body, setBody] = useState(defaultValue)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = body.trim()
    if (!trimmed) return
    onSubmit(trimmed)
    if (!defaultValue) setBody('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        placeholder={placeholder}
        rows={3}
        maxLength={2000}
        className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <div className="flex gap-2 justify-end">
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Отмена
          </Button>
        )}
        <Button type="submit" loading={isPending} disabled={!body.trim()}>
          {submitLabel}
        </Button>
      </div>
    </form>
  )
}
