import { useEffect, useState } from 'react'
import { useFieldArray, useForm } from 'react-hook-form'
import { UNIT_LABELS, type IngredientUnit, type RecipeIngredientRead } from '../api/ingredientsApi'
import { useIngredientSearch } from '../hooks/useIngredients'
import { Button } from '@/shared/ui/Button'
import { Input } from '@/shared/ui/Input'

interface IngredientRowData {
  ingredient_name: string
  amount: string
  unit: IngredientUnit | ''
}

interface FormData {
  ingredients: IngredientRowData[]
}

interface IngredientsFormProps {
  defaultValues?: RecipeIngredientRead[]
  onSubmit: (items: { ingredient_name: string; amount?: number; unit?: IngredientUnit }[]) => void
  isPending: boolean
  error: Error | null
}

function IngredientRow({
  index,
  register,
  remove,
}: {
  index: number
  register: ReturnType<typeof useForm<FormData>>['register']
  remove: () => void
}) {
  const [query, setQuery] = useState('')
  const { data: suggestions } = useIngredientSearch(query)
  const [showSuggestions, setShowSuggestions] = useState(false)

  const { onChange: registerOnChange, onBlur: registerOnBlur, ...nameFieldProps } =
    register(`ingredients.${index}.ingredient_name`)

  return (
    <div className="flex gap-2 items-start">
      <div className="flex-1 relative">
        <Input
          placeholder="Ингредиент"
          {...nameFieldProps}
          onChange={(e) => {
            registerOnChange(e)
            setQuery(e.target.value)
            setShowSuggestions(true)
          }}
          onBlur={(e) => {
            registerOnBlur(e)
            setTimeout(() => setShowSuggestions(false), 150)
          }}
          autoComplete="off"
        />
        {showSuggestions && suggestions && suggestions.length > 0 && (
          <ul className="absolute z-10 w-full bg-white border border-gray-200 rounded-lg shadow-md mt-1 max-h-40 overflow-y-auto">
            {suggestions.map((s) => (
              <li key={s.id}>
                <button
                  type="button"
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => {
                    const input = document.querySelector<HTMLInputElement>(
                      `input[name="ingredients.${index}.ingredient_name"]`
                    )
                    if (input) {
                      input.value = s.name
                      input.dispatchEvent(new Event('input', { bubbles: true }))
                    }
                    setShowSuggestions(false)
                  }}
                >
                  {s.name}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="w-24">
        <Input
          placeholder="Кол-во"
          type="number"
          min={0}
          step="0.1"
          {...register(`ingredients.${index}.amount`)}
        />
      </div>
      <div className="w-28">
        <select
          {...register(`ingredients.${index}.unit`)}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">—</option>
          {(Object.entries(UNIT_LABELS) as [IngredientUnit, string][]).map(([v, l]) => (
            <option key={v} value={v}>{l}</option>
          ))}
        </select>
      </div>
      <button
        type="button"
        onClick={remove}
        className="mt-1 text-gray-400 hover:text-red-500 transition-colors text-lg leading-none"
      >
        ✕
      </button>
    </div>
  )
}

export function IngredientsForm({ defaultValues, onSubmit, isPending, error }: IngredientsFormProps) {
  const { control, register, handleSubmit, reset } = useForm<FormData>({
    defaultValues: { ingredients: [] },
  })
  const { fields, append, remove } = useFieldArray({ control, name: 'ingredients' })

  useEffect(() => {
    if (defaultValues) {
      reset({
        ingredients: defaultValues.map((ri) => ({
          ingredient_name: ri.ingredient.name,
          amount: ri.amount != null ? String(ri.amount) : '',
          unit: (ri.unit ?? '') as IngredientUnit | '',
        })),
      })
    }
  }, [defaultValues, reset])

  const handleFormSubmit = (data: FormData) => {
    const items = data.ingredients
      .filter((i) => i.ingredient_name.trim())
      .map((i) => ({
        ingredient_name: i.ingredient_name.trim(),
        amount: i.amount ? parseFloat(i.amount) : undefined,
        unit: (i.unit || undefined) as IngredientUnit | undefined,
      }))
    onSubmit(items)
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="flex flex-col gap-3">
      {fields.map((field, index) => (
        <IngredientRow
          key={field.id}
          index={index}
          register={register}
          remove={() => remove(index)}
        />
      ))}
      <button
        type="button"
        onClick={() => append({ ingredient_name: '', amount: '', unit: '' })}
        className="text-sm text-blue-600 hover:text-blue-700 text-left"
      >
        + Добавить ингредиент
      </button>
      {error && <p className="text-sm text-red-500">{error.message}</p>}
      <Button type="submit" loading={isPending} disabled={fields.length === 0}>
        Сохранить ингредиенты
      </Button>
    </form>
  )
}
