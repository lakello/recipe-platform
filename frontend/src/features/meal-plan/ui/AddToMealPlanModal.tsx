import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { mealPlanApi, type MealType } from '../api/mealPlanApi'
import { Button } from '@/shared/ui/Button'

const MEAL_TYPES: MealType[] = ['breakfast', 'lunch', 'dinner', 'snack']
const MEAL_LABELS: Record<MealType, string> = {
  breakfast: 'Завтрак',
  lunch: 'Обед',
  dinner: 'Ужин',
  snack: 'Перекус',
}
const DAY_LABELS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

function getMonday(): Date {
  const today = new Date()
  const day = today.getDay()
  const diff = day === 0 ? -6 : 1 - day
  const monday = new Date(today)
  monday.setDate(today.getDate() + diff)
  monday.setHours(0, 0, 0, 0)
  return monday
}

function formatDate(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function addWeeks(d: Date, n: number): Date {
  const r = new Date(d)
  r.setDate(d.getDate() + n * 7)
  return r
}

function formatWeekRange(monday: Date): string {
  const sunday = new Date(monday)
  sunday.setDate(monday.getDate() + 6)
  const fmt = (d: Date) => d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  return `${fmt(monday)} — ${fmt(sunday)} ${sunday.getFullYear()}`
}

function getTodayDayIndex(): number {
  const day = new Date().getDay()
  return day === 0 ? 6 : day - 1
}

export function AddToMealPlanModal({
  recipeId,
  onClose,
}: {
  recipeId: string
  onClose: () => void
}) {
  const [monday, setMonday] = useState(getMonday)
  const [dayOfWeek, setDayOfWeek] = useState(getTodayDayIndex)
  const [mealType, setMealType] = useState<MealType>('lunch')
  const [servings, setServings] = useState(1)
  const [done, setDone] = useState(false)

  const add = useMutation({
    mutationFn: () =>
      mealPlanApi.addItem({
        week_start: formatDate(monday),
        day_of_week: dayOfWeek,
        meal_type: mealType,
        recipe_id: recipeId,
        servings,
      }),
    onSuccess: () => setDone(true),
  })

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6 flex flex-col gap-5"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Добавить в план питания</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
          >
            ×
          </button>
        </div>

        {done ? (
          <div className="text-center py-4">
            <p className="text-green-600 font-medium mb-3">Добавлено в план питания!</p>
            <Button variant="secondary" onClick={onClose}>
              Закрыть
            </Button>
          </div>
        ) : (
          <>
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Неделя</p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setMonday((d) => addWeeks(d, -1))}
                  className="px-2 py-1 rounded bg-gray-100 hover:bg-gray-200 text-sm font-medium"
                >
                  ←
                </button>
                <span className="flex-1 text-center text-sm text-gray-700">
                  {formatWeekRange(monday)}
                </span>
                <button
                  onClick={() => setMonday((d) => addWeeks(d, 1))}
                  className="px-2 py-1 rounded bg-gray-100 hover:bg-gray-200 text-sm font-medium"
                >
                  →
                </button>
              </div>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">День</p>
              <div className="flex flex-wrap gap-1.5">
                {DAY_LABELS.map((label, i) => (
                  <button
                    key={i}
                    onClick={() => setDayOfWeek(i)}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      dayOfWeek === i
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Приём пищи</p>
              <div className="flex flex-wrap gap-1.5">
                {MEAL_TYPES.map((mt) => (
                  <button
                    key={mt}
                    onClick={() => setMealType(mt)}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      mealType === mt
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {MEAL_LABELS[mt]}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Порций</p>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setServings((s) => Math.max(1, s - 1))}
                  disabled={servings <= 1}
                  className="w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-40 text-lg font-medium"
                >
                  −
                </button>
                <span className="text-lg font-semibold min-w-6 text-center">{servings}</span>
                <button
                  onClick={() => setServings((s) => s + 1)}
                  className="w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 hover:bg-gray-200 text-lg font-medium"
                >
                  +
                </button>
              </div>
            </div>

            {add.isError && (
              <p className="text-red-500 text-sm">{(add.error as Error).message}</p>
            )}

            <Button onClick={() => add.mutate()} loading={add.isPending}>
              Добавить
            </Button>
          </>
        )}
      </div>
    </div>
  )
}
