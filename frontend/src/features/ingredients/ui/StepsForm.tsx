import { useEffect, useState } from 'react'
import { useFieldArray, useForm } from 'react-hook-form'
import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import type { RecipeStepRead } from '../api/ingredientsApi'
import { Button } from '@/shared/ui/Button'
import { Input } from '@/shared/ui/Input'

interface StepRowData {
  id: string
  title: string
  description: string
}

interface FormData {
  steps: StepRowData[]
}

interface StepsFormProps {
  defaultValues?: RecipeStepRead[]
  onSubmit: (items: { title: string; description: string }[]) => void
  isPending: boolean
  error: Error | null
}

function SortableStep({
  field,
  index,
  register,
  remove,
  titleMissing,
}: {
  field: { id: string }
  index: number
  register: ReturnType<typeof useForm<FormData>>['register']
  remove: () => void
  titleMissing?: boolean
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: field.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="rounded-xl border border-gray-200 bg-white p-4 flex gap-3"
    >
      <button
        type="button"
        {...attributes}
        {...listeners}
        className="text-gray-300 hover:text-gray-500 cursor-grab active:cursor-grabbing mt-1 shrink-0"
        aria-label="Перетащить"
      >
        ⠿
      </button>
      <div className="flex-1 flex flex-col gap-2">
        <span className="text-xs font-medium text-gray-400">Шаг {index + 1}</span>
        <Input
          placeholder="Заголовок шага *"
          {...register(`steps.${index}.title`)}
          error={titleMissing ? 'Заполните заголовок или удалите этот шаг' : undefined}
        />
        <textarea
          placeholder="Описание (необязательно)"
          rows={3}
          {...register(`steps.${index}.description`)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
      </div>
      <button
        type="button"
        onClick={remove}
        className="text-gray-400 hover:text-red-500 transition-colors text-lg leading-none mt-1 shrink-0"
      >
        ✕
      </button>
    </div>
  )
}

export function StepsForm({ defaultValues, onSubmit, isPending, error }: StepsFormProps) {
  const { control, register, handleSubmit, reset } = useForm<FormData>({
    defaultValues: { steps: [] },
  })
  const { fields, append, remove, move } = useFieldArray({ control, name: 'steps' })
  const [titleMissingIndices, setTitleMissingIndices] = useState<Set<number>>(new Set())

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  useEffect(() => {
    if (defaultValues) {
      reset({
        steps: defaultValues.map((s) => ({
          id: s.id,
          title: s.title ?? '',
          description: s.description,
        })),
      })
    }
  }, [defaultValues, reset])

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    if (over && active.id !== over.id) {
      const oldIndex = fields.findIndex((f) => f.id === active.id)
      const newIndex = fields.findIndex((f) => f.id === over.id)
      move(oldIndex, newIndex)
    }
  }

  const handleFormSubmit = (data: FormData) => {
    const missing = new Set(
      data.steps.reduce<number[]>((acc, s, i) => {
        if (!s.title.trim()) acc.push(i)
        return acc
      }, []),
    )
    setTitleMissingIndices(missing)
    if (missing.size > 0) return

    const items = data.steps.map((s) => ({
      title: s.title.trim(),
      description: s.description.trim(),
    }))
    onSubmit(items)
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="flex flex-col gap-3">
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={fields.map((f) => f.id)}
          strategy={verticalListSortingStrategy}
        >
          {fields.map((field, index) => (
            <SortableStep
              key={field.id}
              field={field}
              index={index}
              register={register}
              titleMissing={titleMissingIndices.has(index)}
              remove={() => {
                remove(index)
                setTitleMissingIndices(new Set())
              }}
            />
          ))}
        </SortableContext>
      </DndContext>

      <button
        type="button"
        onClick={() => append({ id: crypto.randomUUID(), title: '', description: '' })}
        className="text-sm text-blue-600 hover:text-blue-700 text-left"
      >
        + Добавить шаг
      </button>

      {error && <p className="text-sm text-red-500">{error.message}</p>}
      <Button type="submit" loading={isPending} disabled={fields.length === 0}>
        Сохранить шаги
      </Button>
    </form>
  )
}
