import { Container, Typography, Grid, Card, CardContent, Box } from '@mui/material'
import {
  Work as WorkIcon,
  Home as HomeIcon,
  ShoppingCart as ShopIcon,
  Family as FamilyIcon,
  Gavel as GavelIcon,
  Description as ContractIcon,
} from '@mui/icons-material'

const CategoriesPage = () => {
  const categories = [
    {
      id: 'employment',
      name: 'דיני עבודה',
      description: 'פיטורין, זכויות עובדים, חוזי עבודה, שכר ותנאי עבודה',
      icon: <WorkIcon sx={{ fontSize: 48, color: '#2e7d32' }} />,
      color: '#2e7d32',
    },
    {
      id: 'rental',
      name: 'דיני שכירות',
      description: 'חוזי שכירות, זכויות דיירים ומשכירים, בעיות דיור',
      icon: <HomeIcon sx={{ fontSize: 48, color: '#ed6c02' }} />,
      color: '#ed6c02',
    },
    {
      id: 'consumer',
      name: 'זכויות הצרכן',
      description: 'החזרת מוצרים, אחריות, הונאות ומכירות',
      icon: <ShopIcon sx={{ fontSize: 48, color: '#9c27b0' }} />,
      color: '#9c27b0',
    },
    {
      id: 'family',
      name: 'דיני משפחה',
      description: 'גירושין, משמורת ילדים, מזונות וירושה',
      icon: <FamilyIcon sx={{ fontSize: 48, color: '#d32f2f' }} />,
      color: '#d32f2f',
    },
    {
      id: 'small_claims',
      name: 'תביעות קטנות',
      description: 'תביעות עד 37,600 ש"ח, חובות והחזרת כספים',
      icon: <GavelIcon sx={{ fontSize: 48, color: '#1976d2' }} />,
      color: '#1976d2',
    },
    {
      id: 'contracts',
      name: 'חוזים',
      description: 'כתיבה ובדיקת חוזים, הפרת חוזה',
      icon: <ContractIcon sx={{ fontSize: 48, color: '#795548' }} />,
      color: '#795548',
    },
  ]

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
        קטגוריות משפטיות
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        בחר את התחום המשפטי הרלוונטי לך כדי לקבל ייעוץ מותאם ולייצר מסמכים משפטיים.
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {categories.map((category) => (
          <Grid item xs={12} sm={6} md={4} key={category.id}>
            <Card
              sx={{
                height: '100%',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                  borderColor: category.color,
                },
                border: '2px solid transparent',
              }}
            >
              <CardContent sx={{ textAlign: 'center', p: 3 }}>
                <Box sx={{ mb: 2 }}>
                  {category.icon}
                </Box>
                <Typography variant="h6" component="h3" gutterBottom fontWeight="bold">
                  {category.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {category.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 4, p: 3, backgroundColor: '#f8f9fa', borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom>
          לא מצאת את מה שחיפשת?
        </Typography>
        <Typography variant="body2" color="text.secondary">
          תוכל לשאול שאלות כלליות בצ'אט עם הבינה המלאכותית שלנו, והיא תעזור לך לזהות את התחום המשפטי הנכון.
        </Typography>
      </Box>
    </Container>
  )
}

export default CategoriesPage