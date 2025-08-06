import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
  useTheme,
  useMediaQuery,
} from '@mui/material'
import {
  Gavel as GavelIcon,
  Chat as ChatIcon,
  Category as CategoryIcon,
  Description as DocumentIcon,
  Person as PersonIcon,
  Menu as MenuIcon,
} from '@mui/icons-material'

const Navbar = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)

  const menuItems = [
    { path: '/', label: 'בית', icon: <GavelIcon /> },
    { path: '/chat', label: 'צ\'אט AI', icon: <ChatIcon /> },
    { path: '/categories', label: 'קטגוריות', icon: <CategoryIcon /> },
    { path: '/documents', label: 'המסמכים שלי', icon: <DocumentIcon /> },
    { path: '/profile', label: 'פרופיל', icon: <PersonIcon /> },
  ]

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const handleNavigate = (path: string) => {
    navigate(path)
    handleMenuClose()
  }

  return (
    <AppBar position="sticky" sx={{ backgroundColor: '#1976d2' }}>
      <Toolbar>
        <GavelIcon sx={{ mr: 2 }} />
        <Typography
          variant="h6"
          component="div"
          sx={{ flexGrow: 1, fontWeight: 'bold' }}
        >
          LegalGPT - עורך הדין האישי שלך
        </Typography>

        {isMobile ? (
          <>
            <IconButton
              edge="end"
              color="inherit"
              onClick={handleMenuOpen}
              sx={{ ml: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
              transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            >
              {menuItems.map((item) => (
                <MenuItem
                  key={item.path}
                  onClick={() => handleNavigate(item.path)}
                  selected={location.pathname === item.path}
                  sx={{ minWidth: 200 }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {item.icon}
                    {item.label}
                  </Box>
                </MenuItem>
              ))}
            </Menu>
          </>
        ) : (
          <Box sx={{ display: 'flex', gap: 1 }}>
            {menuItems.map((item) => (
              <Button
                key={item.path}
                color="inherit"
                onClick={() => navigate(item.path)}
                startIcon={item.icon}
                sx={{
                  backgroundColor:
                    location.pathname === item.path ? 'rgba(255,255,255,0.1)' : 'transparent',
                  '&:hover': {
                    backgroundColor: 'rgba(255,255,255,0.1)',
                  },
                }}
              >
                {item.label}
              </Button>
            ))}
          </Box>
        )}
      </Toolbar>
    </AppBar>
  )
}

export default Navbar