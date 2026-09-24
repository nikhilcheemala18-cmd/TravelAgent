import { BrowserRouter, Navigate, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import LandingA from './landing/LandingA/LandingA'
import LandingB from './landing/LandingB/LandingB'

/**
 * Top-level route wiring only. Page composition lives in src/pages,
 * feature logic in src/components/src/hooks. Routing is set up now so
 * future pages don't require restructuring this file.
 */
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingA />} />
        <Route path="/landing-a" element={<LandingA />} />
        <Route path="/landing-b" element={<LandingB />} />
        <Route path="/workspace" element={<Home />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
