import { Link, useNavigate } from 'react-router-dom'
import type { Recipe } from '../api/recipesApi'
import { LikeButton } from '@/features/likes/ui/LikeButton'
import { uploadsApi } from '@/features/uploads/api/uploadsApi'
import { UserLink } from '@/shared/ui/UserLink'

const DIFFICULTY_LABELS: Record<string, string> = {
  easy: 'Лёгкий',
  medium: 'Средний',
  hard: 'Сложный',
}

interface RecipeCardProps {
  recipe: Recipe
  isAuthenticated: boolean
}

function PhotoPlaceholder() {
  return (
    <div className="w-full h-full bg-gradient-to-br from-slate-100 to-blue-50 flex items-center justify-center">
      <svg
        className="w-16 h-16 text-slate-300"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.2}
          d="M12 6v6m0 0v6m0-6h6m-6 0H6"
        />
        <circle cx="12" cy="12" r="10" strokeWidth={1.2} />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.2}
          d="M8 14s1.5 2 4 2 4-2 4-2" />
      </svg>
    </div>
  )
}


export function RecipeCard({ recipe, isAuthenticated }: RecipeCardProps) {
  const navigate = useNavigate()

  const handleCardClick = () => {
    navigate(`/recipes/${recipe.id}`)
  }

  const handleLikeClick = (e: React.MouseEvent) => {
    e.stopPropagation()
  }

  const handleCommentClick = (e: React.MouseEvent) => {
    e.stopPropagation()
  }

  return (
    <div
      onClick={handleCardClick}
      className="rounded-2xl bg-white shadow-sm hover:shadow-md transition-shadow cursor-pointer overflow-hidden"
    >
      {/* Фото */}
      <div className="aspect-[16/9] w-full overflow-hidden">
        {recipe.photo ? (
          <img
            src={uploadsApi.getViewUrl(recipe.photo.key)}
            alt={recipe.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <PhotoPlaceholder />
        )}
      </div>

      <div className="p-4 flex flex-col gap-3">
        {/* Мета-теги */}
        <div className="flex flex-wrap gap-1.5">
          {recipe.category && (
            <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
              {recipe.category.name}
            </span>
          )}
          {recipe.difficulty && (
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
              {DIFFICULTY_LABELS[recipe.difficulty]}
            </span>
          )}
          {recipe.servings && (
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
              {recipe.servings} порц.
            </span>
          )}
          {recipe.cooking_time_minutes && (
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
              {recipe.cooking_time_minutes} мин
            </span>
          )}
        </div>

        {/* Название */}
        <h2 className="font-semibold text-gray-900 text-base leading-snug line-clamp-2">
          {recipe.title}
        </h2>

        {/* Автор */}
        <UserLink
          userId={recipe.author.id}
          username={recipe.author.username}
          avatarUrl={recipe.author.avatar_url}
        />

        {/* Лайки и комментарии */}
        <div className="flex items-center gap-2 pt-1 border-t border-gray-100">
          <div onClick={handleLikeClick}>
            <LikeButton
              recipeId={recipe.id}
              likesCount={recipe.likes_count}
              isLiked={recipe.is_liked}
              isAuthenticated={isAuthenticated}
            />
          </div>
          <Link
            to={`/recipes/${recipe.id}#comments`}
            onClick={handleCommentClick}
            className="flex items-center gap-1 text-sm text-gray-400 hover:text-blue-500 transition-colors px-2 py-1 rounded-md"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <span>{recipe.comment_count}</span>
          </Link>
        </div>
      </div>
    </div>
  )
}
