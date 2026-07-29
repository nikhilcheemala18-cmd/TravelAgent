import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'

/**
 * Top-level route wiring only. Page composition lives in src/pages,
 * feature logic in src/components/src/hooks. Routing is set up now so
 * future pages don't require restructuring this file.
 */
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </BrowserRouter>
  )
}
