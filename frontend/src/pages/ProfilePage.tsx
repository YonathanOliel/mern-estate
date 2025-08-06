import { Container, Typography, Box, Paper } from '@mui/material'

const ProfilePage = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
        הפרופיל שלי
      </Typography>
      
      <Paper sx={{ p: 4, minHeight: '70vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Box textAlign="center">
          <Typography variant="h6" color="text.secondary" gutterBottom>
            👤 בבנייה 👤
          </Typography>
          <Typography variant="body1" color="text.secondary">
            כאן תוכל לנהל את הפרופיל האישי שלך ואת ההעדפות שלך.
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            המערכת תכלול: פרטים אישיים, היסטוריית פעילות, והגדרות אישיות.
          </Typography>
        </Box>
      </Paper>
    </Container>
  )
}

export default ProfilePage