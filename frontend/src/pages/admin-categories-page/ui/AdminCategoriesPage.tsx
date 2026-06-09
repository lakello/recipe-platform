import { useState } from 'react'
import { AdminLayout } from '@/widgets/admin-layout'
import {
  useCreateCategory,
  useDeleteCategory,
  useUpdateCategory,
  useCategoriesList,
} from '@/features/categories/hooks/useCategories'
import type { Category } from '@/features/categories/api/categoriesApi'
import {
  useIngredientCategoriesList,
  useCreateIngredientCategory,
  useUpdateIngredientCategory,
  useDeleteIngredientCategory,
} from '@/features/ingredient-categories/hooks/useIngredientCategories'
import type { IngredientCategory } from '@/features/ingredient-categories/api/ingredientCategoriesApi'
import { Button } from '@/shared/ui/Button'
import { Input } from '@/shared/ui/Input'

type Tab = 'recipes' | 'ingredients'

function NameForm({
  onSubmit,
  isPending,
  error,
  submitLabel,
  defaultName = '',
  onCancel,
}: {
  onSubmit: (name: string) => void
  isPending: boolean
  error: Error | null
  submitLabel: string
  defaultName?: string
  onCancel?: () => void
}) {
  const [name, setName] = useState(defaultName)
  return (
    <div className="flex flex-col gap-3">
      <Input label="Название" value={name} onChange={(e) => setName(e.target.value)} />
      {error && <p className="text-sm text-red-500">{error.message}</p>}
      <div className="flex gap-2">
        <Button loading={isPending} onClick={() => onSubmit(name)} disabled={!name.trim()}>
          {submitLabel}
        </Button>
        {onCancel && (
          <Button variant="secondary" onClick={onCancel}>
            Отмена
          </Button>
        )}
      </div>
    </div>
  )
}

function CategoryForm({
  onSubmit,
  isPending,
  error,
  submitLabel,
  defaultName = '',
  defaultDescription = '',
  onCancel,
}: {
  onSubmit: (name: string, description: string) => void
  isPending: boolean
  error: Error | null
  submitLabel: string
  defaultName?: string
  defaultDescription?: string
  onCancel?: () => void
}) {
  const [name, setName] = useState(defaultName)
  const [description, setDescription] = useState(defaultDescription)
  return (
    <div className="flex flex-col gap-3">
      <Input label="Название" value={name} onChange={(e) => setName(e.target.value)} />
      <Input
        label="Описание"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      {error && <p className="text-sm text-red-500">{error.message}</p>}
      <div className="flex gap-2">
        <Button
          loading={isPending}
          onClick={() => onSubmit(name, description)}
          disabled={!name.trim()}
        >
          {submitLabel}
        </Button>
        {onCancel && (
          <Button variant="secondary" onClick={onCancel}>
            Отмена
          </Button>
        )}
      </div>
    </div>
  )
}

function RecipeCategoryRow({ category }: { category: Category }) {
  const [editing, setEditing] = useState(false)
  const { mutate: update, isPending: isUpdating, error: updateError } = useUpdateCategory(category.id)
  const { mutate: remove, isPending: isDeleting } = useDeleteCategory()

  if (editing) {
    return (
      <li className="rounded-xl bg-white p-4 shadow-sm">
        <CategoryForm
          defaultName={category.name}
          defaultDescription={category.description ?? ''}
          onSubmit={(name, description) =>
            update(
              { name, description: description || undefined },
              { onSuccess: () => setEditing(false) },
            )
          }
          isPending={isUpdating}
          error={updateError}
          submitLabel="Сохранить"
          onCancel={() => setEditing(false)}
        />
      </li>
    )
  }

  return (
    <li className="rounded-xl bg-white p-4 shadow-sm flex items-center justify-between gap-3">
      <div className="min-w-0">
        <p className="font-medium text-gray-900">{category.name}</p>
        {category.description && (
          <p className="text-sm text-gray-500 truncate">{category.description}</p>
        )}
        <p className="text-xs text-gray-400 mt-0.5">slug: {category.slug}</p>
      </div>
      <div className="flex gap-2 shrink-0">
        <Button variant="secondary" onClick={() => setEditing(true)}>
          Изменить
        </Button>
        <Button
          variant="danger"
          loading={isDeleting}
          onClick={() => {
            if (confirm(`Удалить категорию "${category.name}"?`)) remove(category.id)
          }}
        >
          Удалить
        </Button>
      </div>
    </li>
  )
}

function IngredientCategoryRow({ category }: { category: IngredientCategory }) {
  const [editing, setEditing] = useState(false)
  const { mutate: update, isPending: isUpdating, error: updateError } =
    useUpdateIngredientCategory(category.id)
  const { mutate: remove, isPending: isDeleting } = useDeleteIngredientCategory()

  if (editing) {
    return (
      <li className="rounded-xl bg-white p-4 shadow-sm">
        <NameForm
          defaultName={category.name}
          onSubmit={(name) => update(name, { onSuccess: () => setEditing(false) })}
          isPending={isUpdating}
          error={updateError}
          submitLabel="Сохранить"
          onCancel={() => setEditing(false)}
        />
      </li>
    )
  }

  return (
    <li className="rounded-xl bg-white p-4 shadow-sm flex items-center justify-between gap-3">
      <p className="font-medium text-gray-900">{category.name}</p>
      <div className="flex gap-2 shrink-0">
        <Button variant="secondary" onClick={() => setEditing(true)}>
          Изменить
        </Button>
        <Button
          variant="danger"
          loading={isDeleting}
          onClick={() => {
            if (confirm(`Удалить категорию "${category.name}"?`)) remove(category.id)
          }}
        >
          Удалить
        </Button>
      </div>
    </li>
  )
}

export function AdminCategoriesPage() {
  const [tab, setTab] = useState<Tab>('recipes')
  const [showForm, setShowForm] = useState(false)

  const { data: recipeCategories, isPending: rcPending, error: rcError } = useCategoriesList()
  const { mutate: createRecipe, isPending: rcCreating, error: rcCreateError } = useCreateCategory()

  const {
    data: ingredientCategories,
    isPending: icPending,
    error: icError,
  } = useIngredientCategoriesList()
  const {
    mutate: createIngredient,
    isPending: icCreating,
    error: icCreateError,
  } = useCreateIngredientCategory()

  return (
    <AdminLayout>
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Управление категориями</h1>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => { setTab('recipes'); setShowForm(false) }}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            tab === 'recipes'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Категории рецептов
        </button>
        <button
          onClick={() => { setTab('ingredients'); setShowForm(false) }}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            tab === 'ingredients'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Категории ингредиентов
        </button>
      </div>

      {/* Add form */}
      <div className="rounded-xl bg-white p-6 shadow-sm mb-6">
        {showForm ? (
          <>
            <h2 className="text-base font-semibold text-gray-900 mb-4">Новая категория</h2>
            {tab === 'recipes' ? (
              <CategoryForm
                onSubmit={(name, description) =>
                  createRecipe(
                    { name, description: description || undefined },
                    { onSuccess: () => setShowForm(false) },
                  )
                }
                isPending={rcCreating}
                error={rcCreateError}
                submitLabel="Создать"
                onCancel={() => setShowForm(false)}
              />
            ) : (
              <NameForm
                onSubmit={(name) =>
                  createIngredient(name, { onSuccess: () => setShowForm(false) })
                }
                isPending={icCreating}
                error={icCreateError}
                submitLabel="Создать"
                onCancel={() => setShowForm(false)}
              />
            )}
          </>
        ) : (
          <Button onClick={() => setShowForm(true)}>+ Добавить категорию</Button>
        )}
      </div>

      {/* List */}
      {tab === 'recipes' && (
        <>
          {rcPending && <p className="text-gray-500">Загрузка...</p>}
          {rcError && <p className="text-red-500">{rcError.message}</p>}
          {recipeCategories?.length === 0 && <p className="text-gray-500">Категорий пока нет.</p>}
          <ul className="flex flex-col gap-3">
            {recipeCategories?.map((c) => <RecipeCategoryRow key={c.id} category={c} />)}
          </ul>
        </>
      )}

      {tab === 'ingredients' && (
        <>
          {icPending && <p className="text-gray-500">Загрузка...</p>}
          {icError && <p className="text-red-500">{icError.message}</p>}
          {ingredientCategories?.length === 0 && (
            <p className="text-gray-500">Категорий пока нет.</p>
          )}
          <ul className="flex flex-col gap-3">
            {ingredientCategories?.map((c) => (
              <IngredientCategoryRow key={c.id} category={c} />
            ))}
          </ul>
        </>
      )}
    </div>
    </AdminLayout>
  )
}
