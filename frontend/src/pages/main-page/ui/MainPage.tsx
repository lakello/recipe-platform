import { Link } from 'react-router-dom'
import { Button } from '@/shared/ui/Button'

export function MainPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50">
      <h1 className="text-4xl font-bold text-gray-900">Recipe Platform</h1>
      <p className="mt-4 text-lg text-gray-500">Платформа для рецептов и планирования питания</p>
      <div className="mt-8 flex gap-4">
        <Link to="/recipes">
          <Button>Перейти к рецептам</Button>
        </Link>
        <Link to="/profile">
          <Button variant="secondary">Профиль</Button>
        </Link>
      </div>
    </div>
  )
}
