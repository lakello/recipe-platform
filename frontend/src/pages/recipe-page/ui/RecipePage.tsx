import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { IngredientsForm } from '@/features/ingredients/ui/IngredientsForm'
import { StepsForm } from '@/features/ingredients/ui/StepsForm'
import {
  useSetRecipeIngredients,
  useSetRecipeSteps,
} from '@/features/ingredients/hooks/useIngredients'
import { UNIT_LABELS } from '@/features/ingredients/api/ingredientsApi'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'
import { useDeleteRecipe, useRecipe, useUpdateRecipe } from '@/features/recipes/hooks/useRecipes'
import { LikeButton } from '@/features/likes/ui/LikeButton'
import { FavoriteButton } from '@/features/likes/ui/FavoriteButton'
import { PhotoUpload } from '@/features/uploads/ui/PhotoUpload'
import { uploadsApi } from '@/features/uploads/api/uploadsApi'
import { useRecipePhotoUpload } from '@/features/uploads/hooks/useUpload'
import { Button } from '@/shared/ui/Button'
import { UserLink } from '@/shared/ui/UserLink'
import { CommentList } from '@/features/comments/ui/CommentList'

const DIFFICULTY_LABELS: Record<string, string> = {
  easy: 'Лёгкий',
  medium: 'Средний',
  hard: 'Сложный',
}

export function RecipePage() {
  const { recipeId } = useParams<{ recipeId: string }>()
  const navigate = useNavigate()
  const { data: recipe, isPending, error } = useRecipe(recipeId!)
  const { data: user } = useCurrentUser()
  const { mutate: update, isPending: isPublishing } = useUpdateRecipe(recipeId!)
  const { mutate: remove, isPending: isDeleting } = useDeleteRecipe()
  const { mutate: setIngredients, isPending: isSavingIngredients, error: ingredientsError } =
    useSetRecipeIngredients(recipeId!)
  const { mutate: setSteps, isPending: isSavingSteps, error: stepsError } =
    useSetRecipeSteps(recipeId!)

  const [editingIngredients, setEditingIngredients] = useState(false)
  const [editingSteps, setEditingSteps] = useState(false)
  const { upload: uploadPhoto, remove: removePhoto, isPending: isPhotoLoading, error: photoError } =
    useRecipePhotoUpload(recipeId!)

  const isAuthor = !!user && !!recipe && user.id === recipe.author_id

  if (isPending)
    return <div className="mx-auto max-w-2xl px-4 py-12 text-gray-500">Загрузка...</div>
  if (error)
    return <div className="mx-auto max-w-2xl px-4 py-12 text-red-500">{error.message}</div>
  if (!recipe) return null

  return (
    <div className="mx-auto max-w-2xl px-4 py-12 flex flex-col gap-6">
      <button
        onClick={() => navigate(-1)}
        className="text-sm text-gray-500 hover:text-gray-700 text-left"
      >
        ← Назад
      </button>

      {/* Основная информация */}
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{recipe.title}</h1>
            {recipe.category && (
              <span className="text-sm text-blue-600 font-medium">{recipe.category.name}</span>
            )}
            <div className="mt-2">
              <UserLink
                userId={recipe.author.id}
                username={recipe.author.username}
                avatarUrl={recipe.author.avatar_url}
                size="md"
              />
            </div>
          </div>
          <div className="flex flex-col gap-2 items-end shrink-0">
            <div className="flex flex-col gap-1 items-end">
              {recipe.status === 'draft' ? (
                <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">
                  Черновик
                </span>
              ) : (
                <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                  Опубликован
                </span>
              )}
              {recipe.visibility === 'private' && (
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                  Приватный
                </span>
              )}
            </div>
            <div className="flex items-center gap-1">
              <LikeButton
                recipeId={recipe.id}
                likesCount={recipe.likes_count}
                isLiked={recipe.is_liked}
                isAuthenticated={!!user}
              />
              <FavoriteButton
                recipeId={recipe.id}
                isFavorited={recipe.is_favorited}
                isAuthenticated={!!user}
              />
            </div>
          </div>
        </div>

        {recipe.photo && (
          <div className="mb-6 rounded-xl overflow-hidden bg-gray-100 max-h-80">
            <img
              src={uploadsApi.getViewUrl(recipe.photo.key)}
              alt={recipe.title}
              className="w-full h-full object-cover"
            />
          </div>
        )}

        {isAuthor && (
          <div className="mb-6">
            <PhotoUpload
              currentUrl={recipe.photo ? uploadsApi.getViewUrl(recipe.photo.key) : undefined}
              onUpload={uploadPhoto}
              onRemove={recipe.photo ? removePhoto : undefined}
              isPending={isPhotoLoading}
              error={photoError}
              label="Добавить фото"
            />
          </div>
        )}

        {recipe.description && (
          <p className="text-gray-700 mb-6 whitespace-pre-line">{recipe.description}</p>
        )}

        <dl className="grid grid-cols-3 gap-4 text-sm mb-6">
          {recipe.cooking_time_minutes && (
            <div>
              <dt className="text-gray-500">Время</dt>
              <dd className="font-medium">{recipe.cooking_time_minutes} мин</dd>
            </div>
          )}
          {recipe.servings && (
            <div>
              <dt className="text-gray-500">Порций</dt>
              <dd className="font-medium">{recipe.servings}</dd>
            </div>
          )}
          {recipe.difficulty && (
            <div>
              <dt className="text-gray-500">Сложность</dt>
              <dd className="font-medium">{DIFFICULTY_LABELS[recipe.difficulty]}</dd>
            </div>
          )}
        </dl>

        {isAuthor && (
          <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-100">
            {recipe.status === 'draft' && (
              <Button loading={isPublishing} onClick={() => update({ status: 'published' })}>
                Опубликовать
              </Button>
            )}
            <Link to={`/recipes/${recipe.id}/edit`} replace>
              <Button variant="secondary">Редактировать</Button>
            </Link>
            <Button
              variant="danger"
              loading={isDeleting}
              onClick={() => {
                if (confirm('Удалить рецепт?')) remove(recipe.id)
              }}
            >
              Удалить
            </Button>
          </div>
        )}
      </div>

      {/* Ингредиенты */}
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Ингредиенты</h2>
          {isAuthor && !editingIngredients && (
            <button
              onClick={() => setEditingIngredients(true)}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Изменить
            </button>
          )}
        </div>

        {editingIngredients ? (
          <IngredientsForm
            defaultValues={recipe.ingredients}
            onSubmit={(items) =>
              setIngredients(items, { onSuccess: () => setEditingIngredients(false) })
            }
            onRemove={(items) => setIngredients(items)}
            isPending={isSavingIngredients}
            error={ingredientsError}
          />
        ) : recipe.ingredients.length === 0 ? (
          <p className="text-gray-400 text-sm">Ингредиенты не добавлены.</p>
        ) : (
          <ul className="divide-y divide-gray-100">
            {recipe.ingredients.map((ri) => (
              <li key={ri.id} className="flex items-center justify-between py-2 text-sm">
                <span className="text-gray-900">{ri.ingredient.name}</span>
                <span className="text-gray-500">
                  {ri.amount != null ? ri.amount : ''}
                  {ri.unit ? ` ${UNIT_LABELS[ri.unit]}` : ''}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Шаги */}
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Приготовление</h2>
          {isAuthor && !editingSteps && (
            <button
              onClick={() => setEditingSteps(true)}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Изменить
            </button>
          )}
        </div>

        {editingSteps ? (
          <StepsForm
            defaultValues={recipe.steps}
            onSubmit={(items) =>
              setSteps(items, { onSuccess: () => setEditingSteps(false) })
            }
            isPending={isSavingSteps}
            error={stepsError}
          />
        ) : recipe.steps.length === 0 ? (
          <p className="text-gray-400 text-sm">Шаги не добавлены.</p>
        ) : (
          <ol className="flex flex-col gap-4">
            {recipe.steps.map((step, i) => (
              <li key={step.id} className="flex gap-4">
                <span className="flex-shrink-0 w-7 h-7 rounded-full bg-blue-600 text-white text-sm font-bold flex items-center justify-center">
                  {i + 1}
                </span>
                <div>
                  {step.title && (
                    <p className="font-medium text-gray-900 mb-1">{step.title}</p>
                  )}
                  <p className="text-gray-700 text-sm whitespace-pre-line">{step.description}</p>
                </div>
              </li>
            ))}
          </ol>
        )}
      </div>
      {/* Комментарии */}
      <CommentList recipeId={recipe.id} currentUser={user} />
    </div>
  )
}
