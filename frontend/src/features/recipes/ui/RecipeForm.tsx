import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Button } from '@/shared/ui/Button'
import { Input } from '@/shared/ui/Input'
import type { Recipe } from '../api/recipesApi'

const schema = z.object({
  title: z.string().min(1, 'Введите название').max(255, 'Максимум 255 символов'),
  description: z.string().optional(),
  visibility: z.enum(['public', 'private']),
  cooking_time_minutes: z.number().int().min(1, 'Минимум 1 минута').optional(),
  servings: z.number().int().min(1, 'Минимум 1 порция').optional(),
  difficulty: z.enum(['easy', 'medium', 'hard']).optional(),
})

export type RecipeFormData = z.infer<typeof schema>

interface RecipeFormProps {
  defaultValues?: Partial<Recipe>
  onSubmit: (data: RecipeFormData) => void
  isPending: boolean
  error: Error | null
  submitLabel: string
}

const DIFFICULTY_OPTIONS = [
  { value: 'easy', label: 'Лёгкий' },
  { value: 'medium', label: 'Средний' },
  { value: 'hard', label: 'Сложный' },
]

export function RecipeForm({ defaultValues, onSubmit, isPending, error, submitLabel }: RecipeFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RecipeFormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: defaultValues?.title ?? '',
      description: defaultValues?.description ?? '',
      visibility: defaultValues?.visibility ?? 'public',
      cooking_time_minutes: defaultValues?.cooking_time_minutes ?? undefined,
      servings: defaultValues?.servings ?? undefined,
      difficulty: defaultValues?.difficulty ?? undefined,
    },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
      <Input label="Название *" error={errors.title?.message} {...register('title')} />

      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Описание</label>
        <textarea
          {...register('description')}
          rows={4}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Видимость</label>
          <select
            {...register('visibility')}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="public">Публичный</option>
            <option value="private">Приватный</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Сложность</label>
          <select
            {...register('difficulty', {
              setValueAs: (v: string) => (v === '' ? undefined : v),
            })}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Не указана</option>
            {DIFFICULTY_OPTIONS.map(({ value, label }) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Время приготовления (мин)"
          type="number"
          min={1}
          error={errors.cooking_time_minutes?.message}
          {...register('cooking_time_minutes', {
            setValueAs: (v: string) => (v === '' ? undefined : parseInt(v, 10)),
          })}
        />
        <Input
          label="Порций"
          type="number"
          min={1}
          error={errors.servings?.message}
          {...register('servings', {
            setValueAs: (v: string) => (v === '' ? undefined : parseInt(v, 10)),
          })}
        />
      </div>

      {error && <p className="text-sm text-red-500">{error.message}</p>}

      <Button type="submit" loading={isPending}>
        {submitLabel}
      </Button>
    </form>
  )
}
