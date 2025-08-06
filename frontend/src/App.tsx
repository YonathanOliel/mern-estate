import { Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'
import Navbar from '@/components/Navbar'
import HomePage from '@/pages/HomePage'
import ChatPage from '@/pages/ChatPage'
import CategoriesPage from '@/pages/CategoriesPage'
import DocumentsPage from '@/pages/DocumentsPage'
import ProfilePage from '@/pages/ProfilePage'

function App() {
  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <Navbar />
      <Box component="main">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/categories" element={<CategoriesPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Routes>
      </Box>
    </Box>
  )
}

export default App