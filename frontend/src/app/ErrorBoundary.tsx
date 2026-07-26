import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  failed: boolean
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { failed: false }

  static getDerivedStateFromError(): State {
    return { failed: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Unhandled React error', error, info)
  }

  render() {
    if (this.state.failed) {
      return (
        <main className="grid min-h-screen place-items-center p-6 text-center">
          <div>
            <h1 className="text-2xl font-bold">Что-то пошло не так</h1>
            <p className="mt-2 text-gray-600">
              Обновите страницу и попробуйте ещё раз.
            </p>
            <button
              className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-white"
              onClick={() => window.location.reload()}
            >
              Обновить страницу
            </button>
          </div>
        </main>
      )
    }
    return this.props.children
  }
}
