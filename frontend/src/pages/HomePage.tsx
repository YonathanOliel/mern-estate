import { useNavigate } from 'react-router-dom'
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
} from '@mui/material'
import {
  Chat as ChatIcon,
  Work as WorkIcon,
  Home as HomeIcon,
  ShoppingCart as ShopIcon,
  Family as FamilyIcon,
  Gavel as GavelIcon,
  AutoAwesome as AIIcon,
} from '@mui/icons-material'

const HomePage = () => {
  const navigate = useNavigate()

  const features = [
    {
      title: 'צ\'אט חכם עם AI',
      description: 'שאל את השאלות המשפטיות שלך בעברית פשוטה וקבל תשובות מקצועיות',
      icon: <ChatIcon sx={{ fontSize: 40, color: '#1976d2' }} />,
      action: () => navigate('/chat'),
      buttonText: 'התחל צ\'אט',
    },
    {
      title: 'דיני עבודה',
      description: 'פיטורין, זכויות עובדים, חוזי עבודה ותנאי עבודה',
      icon: <WorkIcon sx={{ fontSize: 40, color: '#2e7d32' }} />,
      action: () => navigate('/categories'),
      buttonText: 'לקטגוריה',
    },
    {
      title: 'דיני שכירות',
      description: 'חוזי שכירות, זכויות דיירים ומשכירים',
      icon: <HomeIcon sx={{ fontSize: 40, color: '#ed6c02' }} />,
      action: () => navigate('/categories'),
      buttonText: 'לקטגוריה',
    },
    {
      title: 'זכויות הצרכן',
      description: 'החזרת מוצרים, אחריות, הונאות ומכירות',
      icon: <ShopIcon sx={{ fontSize: 40, color: '#9c27b0' }} />,
      action: () => navigate('/categories'),
      buttonText: 'לקטגוריה',
    },
    {
      title: 'דיני משפחה',
      description: 'גירושין, משמורת ילדים, מזונות וירושה',
      icon: <FamilyIcon sx={{ fontSize: 40, color: '#d32f2f' }} />,
      action: () => navigate('/categories'),
      buttonText: 'לקטגוריה',
    },
    {
      title: 'תביעות קטנות',
      description: 'תביעות עד 37,600 ש"ח, חובות והחזרת כספים',
      icon: <GavelIcon sx={{ fontSize: 40, color: '#1976d2' }} />,
      action: () => navigate('/categories'),
      buttonText: 'לקטגוריה',
    },
  ]

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Hero Section */}
      <Box textAlign="center" mb={6}>
        <Typography
          variant="h2"
          component="h1"
          gutterBottom
          sx={{
            fontWeight: 'bold',
            background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 2,
          }}
        >
          🏛️ עורך הדין האישי שלך ⚖️
        </Typography>
        
        <Typography variant="h5" color="text.secondary" paragraph>
          שירותים משפטיים חכמים ונגישים לכולם
        </Typography>
        
        <Typography variant="body1" color="text.secondary" paragraph sx={{ maxWidth: 800, mx: 'auto' }}>
          LegalGPT מאפשרת לך לקבל ייעוץ משפטי מקצועי, ליצור מסמכים משפטיים ולהבין את זכויותיך - 
          הכל בעברית פשוטה ונגישה, ללא צורך בידע משפטי מוקדם.
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap', mt: 3 }}>
          <Chip
            icon={<AIIcon />}
            label="בינה מלאכותית מתקדמת"
            color="primary"
            variant="outlined"
          />
          <Chip
            icon={<ChatIcon />}
            label="תמיכה מלאה בעברית"
            color="secondary"
            variant="outlined"
          />
          <Chip
            label="ייעוץ זמין 24/7"
            color="success"
            variant="outlined"
          />
        </Box>

        <Button
          variant="contained"
          size="large"
          onClick={() => navigate('/chat')}
          sx={{
            mt: 4,
            px: 4,
            py: 1.5,
            fontSize: '1.2rem',
            borderRadius: 2,
            background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
            '&:hover': {
              background: 'linear-gradient(45deg, #1565c0, #1976d2)',
            },
          }}
        >
          התחל עכשיו - זה חינם!
        </Button>
      </Box>

      {/* Features Grid */}
      <Typography variant="h4" component="h2" textAlign="center" mb={4} fontWeight="bold">
        מה אנחנו מציעים?
      </Typography>
      
      <Grid container spacing={3}>
        {features.map((feature, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
              }}
            >
              <CardContent sx={{ flexGrow: 1, textAlign: 'center', pb: 1 }}>
                <Box sx={{ mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h6" component="h3" gutterBottom fontWeight="bold">
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
              <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                <Button
                  variant="outlined"
                  onClick={feature.action}
                  sx={{ borderRadius: 2 }}
                >
                  {feature.buttonText}
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Call to Action */}
      <Box
        sx={{
          mt: 8,
          p: 4,
          textAlign: 'center',
          backgroundColor: '#f8f9fa',
          borderRadius: 3,
          border: '1px solid #e9ecef',
        }}
      >
        <Typography variant="h5" component="h3" gutterBottom fontWeight="bold">
          מוכן להתחיל?
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          פשוט תאר את המצב המשפטי שלך במילים שלך, ואנחנו נעזור לך להבין מה מגיע לך ואיך להמשיך.
        </Typography>
        <Button
          variant="contained"
          size="large"
          onClick={() => navigate('/chat')}
          sx={{ mt: 2, px: 4, borderRadius: 2 }}
        >
          פתח צ'אט עם עורך הדין AI
        </Button>
      </Box>

      {/* Legal Disclaimer */}
      <Box sx={{ mt: 4, p: 2, backgroundColor: '#fff3cd', borderRadius: 2, border: '1px solid #ffeaa7' }}>
        <Typography variant="body2" color="text.secondary" textAlign="center">
          <strong>הערה משפטית:</strong> המידע המוצג באתר זה הוא למטרות הסברה בלבד ואינו מהווה ייעוץ משפטי פורמלי. 
          במקרים מורכבים או חשובים, מומלץ להתייעץ עם עורך דין מוסמך.
        </Typography>
      </Box>
    </Container>
  )
}

export default HomePage