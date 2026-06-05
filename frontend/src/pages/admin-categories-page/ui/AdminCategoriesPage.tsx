import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  useCreateCategory,
  useDeleteCategory,
  useUpdateCategory,
  useCategoriesList,
} from '@/features/categories/hooks/useCategories'
import type { Category } from '@/features/categories/api/categoriesApi'
import { Button } from '@/shared/ui/Button'
import { Input } from '@/shared/ui/Input'

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
      <Input
        label="Название"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
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

function CategoryRow({ category }: { category: Category }) {
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

export function AdminCategoriesPage() {
  const { data: categories, isPending, error } = useCategoriesList()
  const { mutate: create, isPending: isCreating, error: createError } = useCreateCategory()
  const [showForm, setShowForm] = useState(false)

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <div className="flex items-center gap-3 mb-8">
        <Link to="/recipes">
          <Button variant="secondary">← Рецепты</Button>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Управление категориями</h1>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm mb-6">
        {showForm ? (
          <>
            <h2 className="text-base font-semibold text-gray-900 mb-4">Новая категория</h2>
            <CategoryForm
              onSubmit={(name, description) =>
                create(
                  { name, description: description || undefined },
                  { onSuccess: () => setShowForm(false) },
                )
              }
              isPending={isCreating}
              error={createError}
              submitLabel="Создать"
              onCancel={() => setShowForm(false)}
            />
          </>
        ) : (
          <Button onClick={() => setShowForm(true)}>+ Добавить категорию</Button>
        )}
      </div>

      {isPending && <p className="text-gray-500">Загрузка...</p>}
      {error && <p className="text-red-500">{error.message}</p>}

      {categories && categories.length === 0 && (
        <p className="text-gray-500">Категорий пока нет.</p>
      )}

      <ul className="flex flex-col gap-3">
        {categories?.map((category) => (
          <CategoryRow key={category.id} category={category} />
        ))}
      </ul>
    </div>
  )
}
