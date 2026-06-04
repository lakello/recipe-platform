import { type ButtonHTMLAttributes } from 'react'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean
  variant?: 'primary' | 'secondary' | 'danger'
}

const variants = {
  primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-300',
  secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 disabled:bg-gray-50',
  danger: 'bg-red-600 text-white hover:bg-red-700 disabled:bg-red-300',
}

export function Button({
  children,
  loading,
  variant = 'primary',
  disabled,
  ...props
}: Props) {
  return (
    <button
      disabled={disabled ?? loading}
      className={`rounded-md px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed ${variants[variant]}`}
      {...props}
    >
      {loading ? 'Загрузка...' : children}
    </button>
  )
}
