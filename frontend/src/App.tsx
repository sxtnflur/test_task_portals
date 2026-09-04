import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AiWorklog } from './components/AiWorklog'
import { PortalDetailPage } from './pages/PortalDetailPage'
import { PortalsListPage } from './pages/PortalsListPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<PortalsListPage />} />
        <Route path="/portals/:id" element={<PortalDetailPage />} />
      </Routes>
      <AiWorklog />
    </BrowserRouter>
  )
}
