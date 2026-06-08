import { useState, type KeyboardEvent } from 'react'
import { Link } from 'react-router-dom'
import { uploadsApi } from '@/features/uploads/api/uploadsApi'
import { searchApi } from '@/features/search/api/searchApi'
import { Button } from '@/shared/ui/Button'
import { Input } from '@/shared/ui/Input'
import {
  useWeekPlan,
  useAddMealPlanItem,
  useUpdateMealPlanItem,
  useDeleteMealPlanItem,
  useCopyFromWeek,
} from '@/features/meal-plan/hooks/useMealPlan'
import type { MealType, RecipeSummary } from '@/features/meal-plan/api/mealPlanApi'

const DAY_LABELS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
const MEAL_TYPES: MealType[] = ['breakfast', 'lunch', 'dinner', 'snack']
const MEAL_LABELS: Record<MealType, string> = {
  breakfast: 'Завтрак',
  lunch: 'Обед',
  dinner: 'Ужин',
  snack: 'Перекус',
}

function getCurrentMonday(): Date {
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
  const fmt = (d: Date) =>
    d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  return `${fmt(monday)} — ${fmt(sunday)} ${sunday.getFullYear()}`
}

function getDayDate(monday: Date, dayIndex: number): number {
  return new Date(monday.getTime() + dayIndex * 86400000).getDate()
}

// Recipe picker modal
function RecipePicker({
  onSelect,
  onClose,
}: {
  onSelect: (recipe: RecipeSummary) => void
  onClose: () => void
}) {
  const [q, setQ] = useState('')
  const [results, setResults] = useState<RecipeSummary[]>([])
  const [searching, setSearching] = useState(false)

  const doSearch = async (query: string) => {
    if (!query.trim()) {
      setResults([])
      return
    }
    setSearching(true)
    try {
      const res = await searchApi.searchRecipes({ q: query, size: 20 })
      setResults(
        res.items.map((r) => ({
          id: r.id,
          title: r.title,
          cooking_time_minutes: r.cooking_time_minutes,
          servings: r.servings ?? null,
          difficulty: r.difficulty ?? null,
          photo: r.photo ?? null,
          category: r.category ?? null,
        })),
      )
    } catch {
      setResults([])
    } finally {
      setSearching(false)
    }
  }

  const handleKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') doSearch(q)
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4 p-6 flex flex-col gap-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Выбрать рецепт</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
          >
            ×
          </button>
        </div>

        <div className="flex gap-2">
          <div className="flex-1">
            <Input
              placeholder="Название рецепта..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={handleKey}
              autoFocus
            />
          </div>
          <Button type="button" onClick={() => doSearch(q)}>
            Найти
          </Button>
        </div>

        <div className="max-h-72 overflow-y-auto flex flex-col gap-1">
          {searching && (
            <p className="text-gray-400 text-sm text-center py-4">Поиск...</p>
          )}
          {!searching && q && results.length === 0 && (
            <p className="text-gray-400 text-sm text-center py-4">
              Ничего не найдено
            </p>
          )}
          {!searching && !q && (
            <p className="text-gray-400 text-sm text-center py-4">
              Введите название и нажмите Найти
            </p>
          )}
          {results.map((recipe) => (
            <button
              key={recipe.id}
              type="button"
              onClick={() => onSelect(recipe)}
              className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-left transition-colors"
            >
              {recipe.photo ? (
                <img
                  src={uploadsApi.getViewUrl(recipe.photo.key)}
                  alt={recipe.title}
                  className="w-12 h-12 rounded-lg object-cover shrink-0"
                />
              ) : (
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-orange-100 to-amber-200 shrink-0" />
              )}
              <div className="min-w-0">
                <p className="font-medium text-sm text-gray-900 truncate">
                  {recipe.title}
                </p>
                {recipe.cooking_time_minutes && (
                  <p className="text-xs text-gray-400">
                    {recipe.cooking_time_minutes} мин
                  </p>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

function CopyWeekModal({
  targetWeekStart,
  onClose,
}: {
  targetWeekStart: string
  onClose: () => void
}) {
  const [y, mo, d] = targetWeekStart.split('-').map(Number)
  const targetMonday = new Date(y, mo - 1, d)
  const [sourceMonday, setSourceMonday] = useState(() => addWeeks(targetMonday, -1))
  const copy = useCopyFromWeek(targetWeekStart)

  const sourceStr = formatDate(sourceMonday)
  const isSameWeek = sourceStr === targetWeekStart

  const handleCopy = async () => {
    await copy.mutateAsync(sourceStr)
    onClose()
  }

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
          <h2 className="text-lg font-semibold">Копировать план из недели</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
          >
            ×
          </button>
        </div>

        <p className="text-sm text-gray-500">
          Блюда из выбранной недели будут добавлены в текущую открытую неделю.
        </p>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setSourceMonday((d) => addWeeks(d, -1))}
            className="px-2 py-1 rounded bg-gray-100 hover:bg-gray-200 text-sm font-medium"
          >
            ←
          </button>
          <span className="flex-1 text-center text-sm text-gray-700">
            {formatWeekRange(sourceMonday)}
          </span>
          <button
            onClick={() => setSourceMonday((d) => addWeeks(d, 1))}
            className="px-2 py-1 rounded bg-gray-100 hover:bg-gray-200 text-sm font-medium"
          >
            →
          </button>
        </div>

        {isSameWeek && (
          <p className="text-amber-600 text-sm">Нельзя копировать неделю саму в себя.</p>
        )}
        {copy.isError && (
          <p className="text-red-500 text-sm">{(copy.error as Error).message}</p>
        )}

        <div className="flex gap-2">
          <Button variant="secondary" onClick={onClose} className="flex-1">
            Отмена
          </Button>
          <Button
            onClick={handleCopy}
            loading={copy.isPending}
            disabled={isSameWeek}
            className="flex-1"
          >
            Скопировать
          </Button>
        </div>
      </div>
    </div>
  )
}

interface PickerTarget {
  dayOfWeek: number
  mealType: MealType
}

export function MealPlanPage() {
  const [monday, setMonday] = useState(getCurrentMonday)
  const weekStart = formatDate(monday)

  const { data: plan, isLoading, error } = useWeekPlan(weekStart)
  const addItem = useAddMealPlanItem(weekStart)
  const updateItem = useUpdateMealPlanItem(weekStart)
  const deleteItem = useDeleteMealPlanItem(weekStart)

  const [picker, setPicker] = useState<PickerTarget | null>(null)
  const [copyOpen, setCopyOpen] = useState(false)

  const handleSelectRecipe = (recipe: RecipeSummary) => {
    if (!picker) return
    addItem.mutate({
      week_start: weekStart,
      day_of_week: picker.dayOfWeek,
      meal_type: picker.mealType,
      recipe_id: recipe.id,
      servings: 1,
    })
    setPicker(null)
  }

  const itemsFor = (dayOfWeek: number, mealType: MealType) =>
    plan?.items.filter(
      (i) => i.day_of_week === dayOfWeek && i.meal_type === mealType,
    ) ?? []

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-3">
          <Link to="/recipes">
            <Button variant="secondary">← Рецепты</Button>
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">План питания</h1>
        </div>
        <Button variant="secondary" onClick={() => setCopyOpen(true)}>
          Копировать из другой недели
        </Button>
      </div>

      {/* Week navigation */}
      <div className="flex items-center justify-center gap-4 mb-6">
        <button
          onClick={() => setMonday((d) => addWeeks(d, -1))}
          className="px-3 py-1.5 rounded-lg bg-gray-100 hover:bg-gray-200 text-sm font-medium transition-colors"
        >
          ← Пред.
        </button>
        <span className="text-base font-semibold text-gray-700 min-w-48 text-center">
          {formatWeekRange(monday)}
        </span>
        <button
          onClick={() => setMonday((d) => addWeeks(d, 1))}
          className="px-3 py-1.5 rounded-lg bg-gray-100 hover:bg-gray-200 text-sm font-medium transition-colors"
        >
          След. →
        </button>
      </div>

      {isLoading && (
        <p className="text-gray-400 text-center py-12">Загрузка...</p>
      )}
      {error && (
        <p className="text-red-500 text-center py-12">{error.message}</p>
      )}

      {/* Grid */}
      {!isLoading && !error && (
        <div className="overflow-x-auto">
          <div
            className="grid min-w-[700px]"
            style={{ gridTemplateColumns: '80px repeat(7, 1fr)' }}
          >
            {/* Header row */}
            <div />
            {DAY_LABELS.map((label, i) => (
              <div key={i} className="text-center pb-2">
                <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  {label}
                </span>
                <span className="block text-lg font-bold text-gray-800">
                  {getDayDate(monday, i)}
                </span>
              </div>
            ))}

            {/* Meal type rows */}
            {MEAL_TYPES.map((mealType) => (
              <>
                {/* Label */}
                <div
                  key={`label-${mealType}`}
                  className="flex items-start justify-end pr-3 pt-3"
                >
                  <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide rotate-0">
                    {MEAL_LABELS[mealType]}
                  </span>
                </div>

                {/* Day cells */}
                {Array.from({ length: 7 }, (_, dayIndex) => {
                  const items = itemsFor(dayIndex, mealType)
                  return (
                    <div
                      key={`${mealType}-${dayIndex}`}
                      className="border border-gray-100 rounded-lg m-0.5 p-2 min-h-20 flex flex-col gap-1.5 bg-white"
                    >
                      {items.map((item) => (
                        <div
                          key={item.id}
                          className="flex items-start gap-1.5 bg-orange-50 rounded-md p-1.5 group"
                        >
                          {item.recipe.photo ? (
                            <img
                              src={uploadsApi.getViewUrl(item.recipe.photo.key)}
                              alt={item.recipe.title}
                              className="w-8 h-8 rounded object-cover shrink-0"
                            />
                          ) : (
                            <div className="w-8 h-8 rounded bg-gradient-to-br from-orange-100 to-amber-200 shrink-0" />
                          )}
                          <div className="flex-1 min-w-0">
                            <Link
                              to={`/recipes/${item.recipe.id}`}
                              className="text-xs font-medium text-gray-800 leading-tight truncate hover:text-blue-600 transition-colors block"
                              title={item.recipe.title}
                            >
                              {item.recipe.title}
                            </Link>
                            {/* Servings control */}
                            <div className="flex items-center gap-1 mt-0.5">
                              <button
                                onClick={() =>
                                  item.servings > 1 &&
                                  updateItem.mutate({
                                    itemId: item.id,
                                    servings: item.servings - 1,
                                  })
                                }
                                className="w-4 h-4 flex items-center justify-center rounded bg-white text-gray-500 hover:bg-gray-100 text-xs leading-none"
                                disabled={item.servings <= 1}
                              >
                                −
                              </button>
                              <span className="text-xs text-gray-600 min-w-4 text-center">
                                {item.servings}
                              </span>
                              <button
                                onClick={() =>
                                  updateItem.mutate({
                                    itemId: item.id,
                                    servings: item.servings + 1,
                                  })
                                }
                                className="w-4 h-4 flex items-center justify-center rounded bg-white text-gray-500 hover:bg-gray-100 text-xs leading-none"
                              >
                                +
                              </button>
                              <span className="text-xs text-gray-400">п.</span>
                            </div>
                          </div>
                          <button
                            onClick={() => deleteItem.mutate(item.id)}
                            className="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-400 transition-opacity text-base leading-none shrink-0"
                          >
                            ×
                          </button>
                        </div>
                      ))}

                      <button
                        type="button"
                        onClick={() =>
                          setPicker({ dayOfWeek: dayIndex, mealType })
                        }
                        className="mt-auto text-xs text-gray-400 hover:text-blue-500 transition-colors text-center py-0.5"
                      >
                        + Добавить
                      </button>
                    </div>
                  )
                })}
              </>
            ))}
          </div>
        </div>
      )}

      {/* Recipe picker modal */}
      {picker && (
        <RecipePicker
          onSelect={handleSelectRecipe}
          onClose={() => setPicker(null)}
        />
      )}

      {/* Copy week modal */}
      {copyOpen && (
        <CopyWeekModal
          targetWeekStart={weekStart}
          onClose={() => setCopyOpen(false)}
        />
      )}
    </div>
  )
}
