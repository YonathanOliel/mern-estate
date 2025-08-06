import { Container, Typography, Box, Paper } from '@mui/material'

const ChatPage = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
        צ'אט עם עורך הדין AI
      </Typography>
      
      <Paper sx={{ p: 4, minHeight: '70vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Box textAlign="center">
          <Typography variant="h6" color="text.secondary" gutterBottom>
            🚧 בבנייה 🚧
          </Typography>
          <Typography variant="body1" color="text.secondary">
            מערכת הצ'אט עם AI תהיה זמינה בקרוב!
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            כאן תוכל לשאול שאלות משפטיות בעברית פשוטה ולקבל תשובות מקצועיות מהבינה המלאכותית.
          </Typography>
        </Box>
      </Paper>
    </Container>
  )
}

export default ChatPage