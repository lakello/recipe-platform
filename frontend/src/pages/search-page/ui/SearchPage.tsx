import { useState, type FormEvent, type KeyboardEvent } from 'react'
import { Link } from 'react-router-dom'
import { useCategoriesList } from '@/features/categories/hooks/useCategories'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'
import { RecipeCard } from '@/features/recipes/ui/RecipeCard'
import { useSearch } from '@/features/search/hooks/useSearch'
import type { SearchParams } from '@/features/search/api/searchApi'
import type { Difficulty } from '@/features/recipes/api/recipesApi'
import { Button } from '@/shared/ui/Button'
import { Input } from '@/shared/ui/Input'

const DIFFICULTY_OPTIONS: { value: Difficulty; label: string }[] = [
  { value: 'easy', label: 'Лёгкий' },
  { value: 'medium', label: 'Средний' },
  { value: 'hard', label: 'Сложный' },
]

const SORT_OPTIONS: { value: NonNullable<SearchParams['sort']>; label: string }[] = [
  { value: 'relevance', label: 'По релевантности' },
  { value: 'newest', label: 'Сначала новые' },
  { value: 'popular', label: 'По популярности' },
]

function TagInput({
  label,
  tags,
  onAdd,
  onRemove,
  placeholder,
}: {
  label: string
  tags: string[]
  onAdd: (tag: string) => void
  onRemove: (tag: string) => void
  placeholder?: string
}) {
  const [value, setValue] = useState('')

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      const trimmed = value.trim()
      if (trimmed && !tags.includes(trimmed)) onAdd(trimmed)
      setValue('')
    }
  }

  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-sm font-medium text-gray-700">{label}</span>
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {tags.map((tag) => (
            <span
              key={tag}
              className="flex items-center gap-1 text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full"
            >
              {tag}
              <button
                type="button"
                onClick={() => onRemove(tag)}
                className="hover:text-blue-900"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder ?? 'Введите и нажмите Enter'}
        className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
      />
    </div>
  )
}

export function SearchPage() {
  const { data: user } = useCurrentUser()
  const { data: categories } = useCategoriesList()

  const [q, setQ] = useState('')
  const [submittedQ, setSubmittedQ] = useState<string | undefined>()
  const [categoryId, setCategoryId] = useState<string | undefined>()
  const [maxTime, setMaxTime] = useState('')
  const [difficulty, setDifficulty] = useState<Difficulty | undefined>()
  const [includeIngredients, setIncludeIngredients] = useState<string[]>([])
  const [excludeIngredients, setExcludeIngredients] = useState<string[]>([])
  const [sort, setSort] = useState<NonNullable<SearchParams['sort']>>('relevance')

  const searchParams: SearchParams = {
    q: submittedQ,
    categoryId,
    maxTime: maxTime ? parseInt(maxTime, 10) : undefined,
    difficulty,
    includeIngredients,
    excludeIngredients,
    sort,
    size: 50,
  }

  const hasFilters =
    !!submittedQ ||
    !!categoryId ||
    !!maxTime ||
    !!difficulty ||
    includeIngredients.length > 0 ||
    excludeIngredients.length > 0

  const { data, isLoading, error } = useSearch(searchParams, hasFilters)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    setSubmittedQ(q.trim() || undefined)
  }

  const handleFilterChange = () => {
    // filters apply immediately when changed; trigger re-query via state update
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <Link to="/recipes">
            <Button variant="secondary">← Рецепты</Button>
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Поиск рецептов</h1>
        </div>
      </div>

      {/* Поисковая строка */}
      <form onSubmit={handleSubmit} className="flex gap-2 mb-6">
        <div className="flex-1">
          <Input
            placeholder="Название рецепта..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
        <Button type="submit">Найти</Button>
      </form>

      {/* Фильтры */}
      <div className="rounded-xl bg-white p-5 shadow-sm mb-6 flex flex-col gap-5">
        {/* Категория */}
        {categories && categories.length > 0 && (
          <div className="flex flex-col gap-2">
            <span className="text-sm font-medium text-gray-700">Категория</span>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => { setCategoryId(undefined); handleFilterChange() }}
                className={`px-3 py-1 rounded-full text-sm transition-colors ${!categoryId ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
              >
                Все
              </button>
              {categories.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => { setCategoryId(c.id === categoryId ? undefined : c.id); handleFilterChange() }}
                  className={`px-3 py-1 rounded-full text-sm transition-colors ${categoryId === c.id ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                >
                  {c.name}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
          {/* Сложность */}
          <div className="flex flex-col gap-2">
            <span className="text-sm font-medium text-gray-700">Сложность</span>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => { setDifficulty(undefined); handleFilterChange() }}
                className={`px-3 py-1 rounded-full text-sm transition-colors ${!difficulty ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
              >
                Любая
              </button>
              {DIFFICULTY_OPTIONS.map((d) => (
                <button
                  key={d.value}
                  type="button"
                  onClick={() => { setDifficulty(d.value === difficulty ? undefined : d.value); handleFilterChange() }}
                  className={`px-3 py-1 rounded-full text-sm transition-colors ${difficulty === d.value ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>

          {/* Время */}
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-gray-700">
              Макс. время (мин)
            </label>
            <input
              type="number"
              min={1}
              value={maxTime}
              onChange={(e) => { setMaxTime(e.target.value); handleFilterChange() }}
              placeholder="Не ограничено"
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
            />
          </div>

          {/* Сортировка */}
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-gray-700">Сортировка</label>
            <select
              value={sort}
              onChange={(e) => { setSort(e.target.value as typeof sort); handleFilterChange() }}
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none bg-white"
            >
              {SORT_OPTIONS.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Ингредиенты */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <TagInput
            label="Включить ингредиенты"
            tags={includeIngredients}
            onAdd={(tag) => { setIncludeIngredients((prev) => [...prev, tag]); handleFilterChange() }}
            onRemove={(tag) => { setIncludeIngredients((prev) => prev.filter((t) => t !== tag)); handleFilterChange() }}
            placeholder="Напр: курица, чеснок + Enter"
          />
          <TagInput
            label="Исключить ингредиенты"
            tags={excludeIngredients}
            onAdd={(tag) => { setExcludeIngredients((prev) => [...prev, tag]); handleFilterChange() }}
            onRemove={(tag) => { setExcludeIngredients((prev) => prev.filter((t) => t !== tag)); handleFilterChange() }}
            placeholder="Напр: свинина, орехи + Enter"
          />
        </div>
      </div>

      {/* Результаты */}
      {!hasFilters && (
        <div className="text-center py-16 text-gray-400">
          <p className="text-lg mb-2">Введите запрос или выберите фильтр</p>
          <p className="text-sm">Результаты появятся здесь</p>
        </div>
      )}

      {hasFilters && isLoading && (
        <p className="text-gray-500 py-8 text-center">Поиск...</p>
      )}

      {hasFilters && error && (
        <p className="text-red-500 py-8 text-center">{error.message}</p>
      )}

      {hasFilters && data && (
        <>
          <p className="text-sm text-gray-500 mb-4">
            Найдено: {data.total} рецептов
          </p>
          {data.items.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <p className="text-lg mb-2">Ничего не найдено</p>
              <p className="text-sm">Попробуйте изменить запрос или убрать фильтры</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {data.items.map((recipe) => (
                <RecipeCard key={recipe.id} recipe={recipe} isAuthenticated={!!user} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
