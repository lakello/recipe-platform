import { useState, useRef, useEffect, type KeyboardEvent } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { UNIT_LABELS, type IngredientUnit, ingredientsApi } from '@/features/ingredients/api/ingredientsApi'
import type { Ingredient } from '@/features/ingredients/api/ingredientsApi'
import {
  useShoppingList,
  useGenerateShoppingList,
  useAddShoppingListItem,
  useToggleBought,
  useDeleteShoppingListItem,
} from '@/features/shopping-list/hooks/useShoppingList'
import { shoppingListApi } from '@/features/shopping-list/api/shoppingListApi'
import type { ShoppingListItem, GenerationMode } from '@/features/shopping-list/api/shoppingListApi'
import { Button } from '@/shared/ui/Button'
import { Input } from '@/shared/ui/Input'

// --- Date helpers ---

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
  const fmt = (d: Date) => d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  return `${fmt(monday)} — ${fmt(sunday)} ${sunday.getFullYear()}`
}

const DAY_LABELS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

function formatAmount(amount: number | null, unit: string | null): string {
  if (amount == null) return ''
  const label = unit ? (UNIT_LABELS[unit as IngredientUnit] ?? unit) : ''
  return `${amount % 1 === 0 ? amount : amount.toFixed(3).replace(/\.?0+$/, '')} ${label}`.trim()
}

// --- Generation popup ---

function GenerateModal({
  onClose,
  onGenerate,
  isPending,
  error,
}: {
  onClose: () => void
  onGenerate: (mode: GenerationMode, dates?: string[]) => void
  isPending: boolean
  error: Error | null
}) {
  const [mode, setMode] = useState<GenerationMode>('today')
  const [monday, setMonday] = useState(getCurrentMonday)
  const [selectedDays, setSelectedDays] = useState<Set<string>>(new Set())

  const today = formatDate(new Date())

  const toggleDay = (dateStr: string) => {
    setSelectedDays((prev) => {
      const next = new Set(prev)
      if (next.has(dateStr)) {
        next.delete(dateStr)
      } else {
        next.add(dateStr)
      }
      return next
    })
  }

  const handleSubmit = () => {
    if (mode === 'today') {
      onGenerate('today')
    } else if (mode === 'week') {
      onGenerate('week')
    } else {
      if (selectedDays.size === 0) return
      onGenerate('custom', Array.from(selectedDays).sort())
    }
  }

  const canSubmit =
    mode !== 'custom' || selectedDays.size > 0

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4 p-6 flex flex-col gap-5"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Генерация списка покупок</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
        </div>

        {/* Mode selector */}
        <div className="flex flex-col gap-2">
          {(
            [
              { value: 'today', label: 'Только сегодня' },
              { value: 'week', label: 'Следующие 7 дней (включая сегодня)' },
              { value: 'custom', label: 'Выбрать дни вручную' },
            ] as { value: GenerationMode; label: string }[]
          ).map(({ value, label }) => (
            <label
              key={value}
              className="flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer transition-colors hover:bg-gray-50"
              style={{ borderColor: mode === value ? '#2563eb' : '#e5e7eb' }}
            >
              <input
                type="radio"
                name="mode"
                value={value}
                checked={mode === value}
                onChange={() => setMode(value)}
                className="accent-blue-600"
              />
              <span className="text-sm font-medium text-gray-800">{label}</span>
            </label>
          ))}
        </div>

        {/* Custom day picker */}
        {mode === 'custom' && (
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setMonday((d) => addWeeks(d, -1))}
                className="px-2 py-1 rounded bg-gray-100 hover:bg-gray-200 text-sm font-medium"
              >←</button>
              <span className="flex-1 text-center text-sm text-gray-700">{formatWeekRange(monday)}</span>
              <button
                onClick={() => setMonday((d) => addWeeks(d, 1))}
                className="px-2 py-1 rounded bg-gray-100 hover:bg-gray-200 text-sm font-medium"
              >→</button>
            </div>
            <div className="grid grid-cols-7 gap-1">
              {DAY_LABELS.map((label, i) => {
                const d = new Date(monday)
                d.setDate(monday.getDate() + i)
                const dateStr = formatDate(d)
                const checked = selectedDays.has(dateStr)
                const isToday = dateStr === today
                return (
                  <button
                    key={i}
                    onClick={() => toggleDay(dateStr)}
                    className={`flex flex-col items-center py-2 rounded-lg text-xs font-medium transition-colors border ${
                      checked
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <span>{label}</span>
                    <span className={`mt-0.5 text-sm font-bold ${isToday && !checked ? 'text-blue-600' : ''}`}>
                      {d.getDate()}
                    </span>
                  </button>
                )
              })}
            </div>
            {selectedDays.size > 0 && (
              <p className="text-xs text-gray-500 text-center">
                Выбрано дней: {selectedDays.size}
              </p>
            )}
          </div>
        )}

        {error && <p className="text-red-500 text-sm">{error.message}</p>}

        <div className="flex gap-2">
          <Button variant="secondary" onClick={onClose} className="flex-1">
            Отмена
          </Button>
          <Button
            onClick={handleSubmit}
            loading={isPending}
            disabled={!canSubmit}
            className="flex-1"
          >
            Создать
          </Button>
        </div>
      </div>
    </div>
  )
}

// --- Manual add with autocomplete ---

function AddItemForm({ onDone }: { onDone: () => void }) {
  const [name, setName] = useState('')
  const [amount, setAmount] = useState('')
  const [unit, setUnit] = useState('')
  const [suggestions, setSuggestions] = useState<Ingredient[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [selectedIngredientId, setSelectedIngredientId] = useState<string | undefined>()
  const containerRef = useRef<HTMLDivElement>(null)

  const addItem = useAddShoppingListItem()

  // Search based on the last word
  useEffect(() => {
    const words = name.split(/\s+/)
    const lastWord = words[words.length - 1]
    const timer = setTimeout(async () => {
      if (!lastWord.trim()) {
        setSuggestions([])
        setShowSuggestions(false)
        return
      }
      try {
        const results = await ingredientsApi.search(lastWord)
        setSuggestions(results)
        setShowSuggestions(results.length > 0)
      } catch {
        setSuggestions([])
      }
    }, 200)
    return () => clearTimeout(timer)
  }, [name])

  const handleSelectSuggestion = (ingredient: Ingredient) => {
    setSelectedIngredientId(ingredient.id)
    setName(ingredient.name)
    setShowSuggestions(false)
    setSuggestions([])
    // Auto-submit with just the ingredient
    addItem.mutate(
      { ingredient_id: ingredient.id, name: ingredient.name },
      { onSuccess: onDone },
    )
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') setShowSuggestions(false)
  }

  const handleSubmit = () => {
    if (!name.trim()) return
    addItem.mutate(
      {
        ingredient_id: selectedIngredientId,
        name: name.trim(),
        amount: amount ? parseFloat(amount) : undefined,
        unit: unit || undefined,
      },
      { onSuccess: onDone },
    )
  }

  return (
    <div className="flex flex-col gap-3" ref={containerRef}>
      <div className="relative">
        <Input
          label="Название"
          value={name}
          onChange={(e) => {
            setName(e.target.value)
            setSelectedIngredientId(undefined)
          }}
          onKeyDown={handleKeyDown}
          autoFocus
        />
        {showSuggestions && (
          <div className="absolute z-10 left-0 right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
            {suggestions.map((s) => (
              <button
                key={s.id}
                type="button"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => handleSelectSuggestion(s)}
                className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center justify-between"
              >
                <span>{s.name}</span>
                {s.category && (
                  <span className="text-xs text-gray-400">{s.category.name}</span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
      <div className="flex gap-2">
        <div className="flex-1">
          <Input
            label="Количество"
            type="number"
            min="0"
            step="any"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="напр. 500"
          />
        </div>
        <div className="flex-1">
          <Input
            label="Единица"
            value={unit}
            onChange={(e) => setUnit(e.target.value)}
            placeholder="г, кг, шт..."
          />
        </div>
      </div>
      {addItem.isError && (
        <p className="text-red-500 text-sm">{(addItem.error as Error).message}</p>
      )}
      <div className="flex gap-2">
        <Button onClick={handleSubmit} loading={addItem.isPending} disabled={!name.trim()}>
          Добавить
        </Button>
        <Button variant="secondary" onClick={onDone}>
          Отмена
        </Button>
      </div>
    </div>
  )
}

// --- Edit item modal ---

function EditItemModal({
  item,
  onClose,
}: {
  item: ShoppingListItem
  onClose: () => void
}) {
  const [amount, setAmount] = useState(item.amount != null ? String(item.amount) : '')
  const [unit, setUnit] = useState(item.unit ?? '')
  const qc = useQueryClient()

  const { mutate: save, isPending, error } = useMutation({
    mutationFn: (data: { amount?: number; unit?: string }) =>
      shoppingListApi.updateItem(item.id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['shopping-list'] })
      onClose()
    },
  })

  const handleSave = () => {
    const payload: { amount?: number; unit?: string } = {}
    if (amount !== '') payload.amount = parseFloat(amount)
    if (unit !== '') payload.unit = unit
    save(payload)
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4 p-6 flex flex-col gap-5"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wide mb-0.5">Редактирование</p>
            <h2 className="text-lg font-semibold text-gray-900">{item.name}</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
        </div>

        <div className="flex gap-3">
          <div className="flex-1 min-w-0">
            <Input
              label="Количество"
              type="number"
              min="0"
              step="any"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="напр. 500"
              autoFocus
            />
          </div>
          <div className="flex-1 min-w-0">
            <Input
              label="Единица"
              value={unit}
              onChange={(e) => setUnit(e.target.value)}
              placeholder="г, кг, шт..."
            />
          </div>
        </div>

        {error && <p className="text-red-500 text-sm">{(error as Error).message}</p>}

        <div className="flex gap-3">
          <Button variant="secondary" onClick={onClose} className="flex-1">Отмена</Button>
          <Button onClick={handleSave} loading={isPending} className="flex-1">Сохранить</Button>
        </div>
      </div>
    </div>
  )
}

// --- Item row ---

function ItemRow({ item }: { item: ShoppingListItem }) {
  const toggle = useToggleBought()
  const remove = useDeleteShoppingListItem()
  const [editOpen, setEditOpen] = useState(false)

  return (
    <>
      <div
        className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors group ${
          item.is_bought ? 'bg-gray-50 opacity-60' : 'bg-white'
        }`}
      >
        <input
          type="checkbox"
          checked={item.is_bought}
          onChange={() => toggle.mutate({ itemId: item.id, is_bought: !item.is_bought })}
          className="w-4 h-4 rounded accent-blue-600 cursor-pointer shrink-0"
        />
        <div className="flex-1 min-w-0">
          <button
            onClick={() => setEditOpen(true)}
            className={`text-sm font-medium text-left hover:underline decoration-dotted underline-offset-2 ${
              item.is_bought ? 'line-through text-gray-400' : 'text-gray-900'
            }`}
          >
            {item.name}
          </button>
          {item.amount != null && (
            <span className="text-xs text-gray-400 ml-2">
              {formatAmount(item.amount, item.unit)}
            </span>
          )}
        </div>
        <button
          onClick={() => remove.mutate(item.id)}
          className="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-400 transition-opacity text-lg leading-none shrink-0"
          title="Удалить"
        >
          ×
        </button>
      </div>
      {editOpen && <EditItemModal item={item} onClose={() => setEditOpen(false)} />}
    </>
  )
}

// --- Main page ---

export function ShoppingListPage() {
  const { data: list, isLoading, error } = useShoppingList()
  const generate = useGenerateShoppingList()
  const [generateOpen, setGenerateOpen] = useState(false)
  const [addOpen, setAddOpen] = useState(false)

  const handleGenerate = (mode: GenerationMode, dates?: string[]) => {
    generate.mutate({ mode, dates }, { onSuccess: () => setGenerateOpen(false) })
  }

  // Group items by ingredient category
  const grouped = (() => {
    if (!list) return []
    const map = new Map<string, ShoppingListItem[]>()
    for (const item of list.items) {
      const cat = item.ingredient?.category?.name ?? 'Без категории'
      if (!map.has(cat)) map.set(cat, [])
      map.get(cat)!.push(item)
    }
    // "Без категории" goes last
    const result: { category: string; items: ShoppingListItem[] }[] = []
    const sorted = Array.from(map.entries()).sort(([a], [b]) => {
      if (a === 'Без категории') return 1
      if (b === 'Без категории') return -1
      return a.localeCompare(b, 'ru')
    })
    for (const [category, items] of sorted) {
      result.push({ category, items })
    }
    return result
  })()

  const totalItems = list?.items.length ?? 0
  const boughtCount = list?.items.filter((i) => i.is_bought).length ?? 0

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-3">
          <Link to="/recipes">
            <Button variant="secondary">← Рецепты</Button>
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Список покупок</h1>
        </div>
        <Button onClick={() => setGenerateOpen(true)}>Сгенерировать</Button>
      </div>

      {/* Generation status */}
      {generate.isPending && (
        <div className="mb-4 px-4 py-3 rounded-lg bg-blue-50 text-blue-700 text-sm font-medium">
          Генерирую список покупок...
        </div>
      )}

      {/* Last generated info */}
      {list?.last_generated_at && !generate.isPending && (
        <p className="text-xs text-gray-400 mb-4">
          Последняя генерация:{' '}
          {new Date(list.last_generated_at).toLocaleString('ru-RU', {
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      )}

      {/* Progress */}
      {totalItems > 0 && (
        <div className="mb-4 flex items-center gap-3">
          <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 rounded-full transition-all"
              style={{ width: `${(boughtCount / totalItems) * 100}%` }}
            />
          </div>
          <span className="text-sm text-gray-500 shrink-0">
            {boughtCount} / {totalItems}
          </span>
        </div>
      )}

      {isLoading && <p className="text-gray-400 text-center py-12">Загрузка...</p>}
      {error && <p className="text-red-500 text-center py-12">{error.message}</p>}

      {/* Items grouped by category */}
      {!isLoading && !error && (
        <div className="flex flex-col gap-6">
          {grouped.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              <p className="text-lg mb-2">Список пуст</p>
              <p className="text-sm">Нажмите «Сгенерировать» или добавьте товар вручную</p>
            </div>
          )}

          {grouped.map(({ category, items }) => (
            <div key={category}>
              <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                {category}
              </h2>
              <div className="rounded-xl border border-gray-100 overflow-hidden divide-y divide-gray-50">
                {items.map((item) => (
                  <ItemRow key={item.id} item={item} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Manual add */}
      <div className="mt-6">
        {addOpen ? (
          <div className="rounded-xl bg-white border border-gray-200 p-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Добавить вручную</h3>
            <AddItemForm onDone={() => setAddOpen(false)} />
          </div>
        ) : (
          <button
            onClick={() => setAddOpen(true)}
            className="w-full py-3 rounded-xl border-2 border-dashed border-gray-200 text-sm text-gray-400 hover:border-blue-300 hover:text-blue-500 transition-colors"
          >
            + Добавить вручную
          </button>
        )}
      </div>

      {/* Modals */}
      {generateOpen && (
        <GenerateModal
          onClose={() => setGenerateOpen(false)}
          onGenerate={handleGenerate}
          isPending={generate.isPending}
          error={generate.error}
        />
      )}
    </div>
  )
}
