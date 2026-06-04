import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { QueryProvider } from './providers/QueryProvider'
import { MainPage } from '@/pages/main-page'

export function App() {
  return (
    <QueryProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainPage />} />
        </Routes>
      </BrowserRouter>
    </QueryProvider>
  )
}
