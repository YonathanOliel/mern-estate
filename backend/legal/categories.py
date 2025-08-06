import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class LegalCategory(Enum):
    """קטגוריות משפטיות עיקריות"""
    EMPLOYMENT = "employment"
    RENTAL = "rental" 
    CONSUMER = "consumer"
    FAMILY = "family"
    SMALL_CLAIMS = "small_claims"
    CONTRACTS = "contracts"
    REAL_ESTATE = "real_estate"
    CORPORATE = "corporate"
    CRIMINAL = "criminal"
    UNKNOWN = "unknown"

@dataclass
class CategoryMatch:
    """תוצאת התאמת קטגוריה"""
    category: LegalCategory
    confidence: float
    matched_keywords: List[str]
    context_clues: List[str]

class LegalCategoryDetector:
    """
    מזהה קטגוריות משפטיות מתוך טקסט עברי
    משתמש בכללי NLP ומילות מפתח לזיהוי מדויק
    """
    
    def __init__(self):
        """אתחול המזהה עם מילות מפתח וכללים לכל קטגוריה"""
        
        self.category_keywords = {
            LegalCategory.EMPLOYMENT: {
                "primary": [
                    "עבודה", "מעסיק", "עובד", "פיטורין", "שכר", "משכורת",
                    "חוזה עבודה", "הודעה מוקדמת", "פיצויי פיטורין",
                    "ביטוח לאומי", "מס הכנסה", "שעות נוספות", "חופשה",
                    "מחלה", "לידה", "הריון", "הטרדה מינית", "אפליה"
                ],
                "secondary": [
                    "בוס", "מנהל", "משרד", "חברה", "ארגון", "מפעל",
                    "עבודה במשמרות", "עבודה בשעות נוספות", "תלוש שכר",
                    "זכויות עובדים", "ועד עובדים", "איגוד מקצועי"
                ],
                "context": [
                    "פוטרו אותי", "עפו עלי", "זרקו אותי מהעבודה",
                    "לא משלמים לי", "עובד בלי חוזה", "עבודה שחורה",
                    "מעסיק לא הוגן", "תנאי עבודה קשים"
                ]
            },
            
            LegalCategory.RENTAL: {
                "primary": [
                    "שכירות", "דירה", "בית", "נכס", "משכיר", "שוכר",
                    "דייר", "חוזה שכירות", "שכר דירה", "פיקדון",
                    "ארנונה", "ועד בית", "תחזוקה", "תיקונים", "פינוי"
                ],
                "secondary": [
                    "בעל הבית", "בעלת הבית", "דירת מגורים",
                    "דירה להשכרה", "שכירות ארוכת טווח",
                    "הגנת הדייר", "עליית שכירות"
                ],
                "context": [
                    "בעיות עם בעל הבית", "רוצה לעזוב את הדירה",
                    "בעל הבית לא מתקן", "העלו לי שכירות",
                    "רוצים לפנות אותי", "בעיות ברקיעות"
                ]
            },
            
            LegalCategory.CONSUMER: {
                "primary": [
                    "צרכן", "קנייה", "מוצר", "שירות", "חנות", "חברה",
                    "אחריות", "החזרה", "ביטול עסקה", "פגם", "ליקוי",
                    "הונאה", "פרסום מטעה", "מכירה בדלת הבית"
                ],
                "secondary": [
                    "קבלה", "חשבונית", "כרטיס אשראי", "תשלומים",
                    "הזמנה", "משלוח", "אינטרנט", "אונליין", "טלפון"
                ],
                "context": [
                    "קניתי משהו ויש בעיה", "המוצר לא עובד",
                    "רוצה להחזיר", "החברה לא עונה", "לא מכבדים אחריות",
                    "רימו אותי", "שילמתי ולא קיבלתי"
                ]
            },
            
            LegalCategory.FAMILY: {
                "primary": [
                    "משפחה", "נישואין", "גירושין", "ילדים", "אלמנות",
                    "מזונות", "משמורת", "חלוקת רכוש", "הסכם ממון",
                    "כתובה", "גט", "בית דין רבני"
                ],
                "secondary": [
                    "בן זוג", "אשה", "בעל", "אמא", "אבא", "הורים",
                    "ירושה", "צוואה", "אפוטרופסות"
                ],
                "context": [
                    "רוצה להתגרש", "בעיות במשפחה", "בן הזוג שלי",
                    "הילדים שלי", "לא רואה את הילדים", "ירושה מההורים"
                ]
            },
            
            LegalCategory.SMALL_CLAIMS: {
                "primary": [
                    "תביעה קטנה", "תביעות קטנות", "בית משפט השלום",
                    "חוב", "נזק", "פיצוי", "כסף", "תשלום", "החזר"
                ],
                "secondary": [
                    "משפט", "תביעה", "בית דין", "בורר", "גישור",
                    "הוצאה לפועל", "עיקול", "הקפאת חשבון"
                ],
                "context": [
                    "חייבים לי כסף", "לא משלמים לי", "רוצה לתבוע",
                    "איך תובעים", "כמה עולה תביעה", "נגרם לי נזק"
                ]
            }
        }
        
        # Negative indicators - words that might indicate other categories
        self.negative_indicators = {
            LegalCategory.EMPLOYMENT: ["דירה", "בית", "שכירות", "קנייה"],
            LegalCategory.RENTAL: ["עבודה", "מעסיק", "קנייה", "מוצר"],
            LegalCategory.CONSUMER: ["עבודה", "דירה", "שכירות", "נישואין"]
        }

    async def detect_category(self, text: str) -> str:
        """
        זיהוי הקטגוריה המשפטית העיקרית מתוך הטקסט
        
        Args:
            text: הטקסט לניתוח
            
        Returns:
            שם הקטגוריה שזוהתה
        """
        try:
            matches = await self._analyze_text(text)
            
            if not matches:
                return LegalCategory.UNKNOWN.value
            
            # Sort by confidence and return the highest
            best_match = max(matches, key=lambda m: m.confidence)
            
            logger.info(f"Detected category: {best_match.category.value} "
                       f"(confidence: {best_match.confidence:.2f})")
            
            return best_match.category.value
            
        except Exception as e:
            logger.error(f"Error detecting legal category: {str(e)}")
            return LegalCategory.UNKNOWN.value

    async def get_all_categories(self) -> List[Dict[str, Any]]:
        """קבלת רשימת כל הקטגוריות הזמינות עם תיאורים"""
        categories = [
            {
                "id": LegalCategory.EMPLOYMENT.value,
                "name": "דיני עבודה",
                "description": "פיטורין, זכויות עובדים, חוזי עבודה, שכר ותנאי עבודה",
                "icon": "👔",
                "examples": ["פוטרו אותי מהעבודה", "בעיות עם המעסיק", "זכויות עובדים"]
            },
            {
                "id": LegalCategory.RENTAL.value,
                "name": "דיני שכירות",
                "description": "חוזי שכירות, זכויות דיירים ומשכירים, בעיות דיור",
                "icon": "🏠",
                "examples": ["בעיות עם בעל הבית", "חוזה שכירות", "פינוי דירה"]
            },
            {
                "id": LegalCategory.CONSUMER.value,
                "name": "זכויות הצרכן",
                "description": "החזרת מוצרים, אחריות, הונאות ומכירות",
                "icon": "🛒",
                "examples": ["מוצר פגום", "רוצה להחזיר", "בעיות עם חנות"]
            },
            {
                "id": LegalCategory.FAMILY.value,
                "name": "דיני משפחה",
                "description": "גירושין, משמורת ילדים, מזונות וירושה",
                "icon": "👨‍👩‍👧‍👦",
                "examples": ["רוצה להתגרש", "משמורת ילדים", "בעיות במשפחה"]
            },
            {
                "id": LegalCategory.SMALL_CLAIMS.value,
                "name": "תביעות קטנות",
                "description": "תביעות עד 37,600 ש\"ח, חובות וחזרת כספים",
                "icon": "⚖️",
                "examples": ["חייבים לי כסף", "רוצה לתבוע", "נגרם נזק"]
            },
            {
                "id": LegalCategory.CONTRACTS.value,
                "name": "חוזים",
                "description": "כתיבה ובדיקת חוזים, הפרת חוזה",
                "icon": "📄",
                "examples": ["רוצה לכתוב חוזה", "הפרת חוזה", "בדיקת חוזה"]
            }
        ]
        
        return categories

    async def suggest_related_categories(self, primary_category: str) -> List[str]:
        """הצעת קטגוריות קשורות לקטגוריה הראשית"""
        related_categories = {
            LegalCategory.EMPLOYMENT.value: [
                LegalCategory.CONTRACTS.value,
                LegalCategory.SMALL_CLAIMS.value
            ],
            LegalCategory.RENTAL.value: [
                LegalCategory.CONTRACTS.value,
                LegalCategory.CONSUMER.value,
                LegalCategory.SMALL_CLAIMS.value
            ],
            LegalCategory.CONSUMER.value: [
                LegalCategory.SMALL_CLAIMS.value,
                LegalCategory.CONTRACTS.value
            ],
            LegalCategory.FAMILY.value: [
                LegalCategory.REAL_ESTATE.value,
                LegalCategory.CONTRACTS.value
            ]
        }
        
        return related_categories.get(primary_category, [])

    async def _analyze_text(self, text: str) -> List[CategoryMatch]:
        """ניתוח מפורט של הטקסט לזיהוי קטגוריות"""
        text_lower = text.lower()
        matches = []
        
        for category, keywords in self.category_keywords.items():
            match = await self._calculate_category_match(text_lower, category, keywords)
            if match.confidence > 0.1:  # Minimum threshold
                matches.append(match)
        
        return matches

    async def _calculate_category_match(
        self, 
        text: str, 
        category: LegalCategory, 
        keywords: Dict[str, List[str]]
    ) -> CategoryMatch:
        """חישוב התאמה לקטגוריה ספציפית"""
        
        matched_keywords = []
        context_clues = []
        score = 0.0
        
        # Check primary keywords (high weight)
        for keyword in keywords.get("primary", []):
            if keyword.lower() in text:
                matched_keywords.append(keyword)
                score += 3.0
        
        # Check secondary keywords (medium weight)  
        for keyword in keywords.get("secondary", []):
            if keyword.lower() in text:
                matched_keywords.append(keyword)
                score += 1.5
        
        # Check context clues (medium-high weight)
        for context in keywords.get("context", []):
            if context.lower() in text:
                context_clues.append(context)
                score += 2.0
        
        # Apply negative indicators (reduce score)
        negative_words = self.negative_indicators.get(category, [])
        for neg_word in negative_words:
            if neg_word.lower() in text:
                score *= 0.7  # Reduce score by 30%
        
        # Normalize confidence score (0-1)
        max_possible_score = len(keywords.get("primary", [])) * 3.0
        confidence = min(score / max_possible_score, 1.0) if max_possible_score > 0 else 0.0
        
        return CategoryMatch(
            category=category,
            confidence=confidence,
            matched_keywords=matched_keywords,
            context_clues=context_clues
        )

    def get_category_info(self, category_id: str) -> Optional[Dict[str, Any]]:
        """קבלת מידע מפורט על קטגוריה ספציפית"""
        category_info = {
            LegalCategory.EMPLOYMENT.value: {
                "name": "דיני עבודה",
                "description": "כל הנוגע לזכויות עובדים, פיטורין, תנאי עבודה ויחסי עבודה",
                "common_issues": [
                    "פיטורין לא חוקיים",
                    "אי תשלום שכר",
                    "הפרת זכויות עובדים",
                    "אפליה במקום העבודה",
                    "תאונות עבודה"
                ],
                "typical_documents": [
                    "מכתב התראה למעסיק",
                    "תביעה לבית הדין לעבודה",
                    "חוזה עבודה",
                    "מכתב התפטרות"
                ],
                "relevant_laws": [
                    "חוק הגנת השכר",
                    "חוק שעות עבודה ומנוחה",
                    "חוק פיצויי פיטורין",
                    "חוק שכר שווה"
                ]
            },
            
            LegalCategory.RENTAL.value: {
                "name": "דיני שכירות",
                "description": "זכויות וחובות של שוכרים ומשכירים, חוזי שכירות ובעיות דיור",
                "common_issues": [
                    "עליית שכירות לא חוקית",
                    "בעיות תחזוקה",
                    "פינוי לא חוקי",
                    "החזרת פיקדון",
                    "הפרת תנאי החוזה"
                ],
                "typical_documents": [
                    "חוזה שכירות",
                    "מכתב התראה לבעל הבית",
                    "תביעה להחזרת פיקדון",
                    "בקשה לפינוי"
                ],
                "relevant_laws": [
                    "חוק הגנת הדייר",
                    "חוק השכירות",
                    "חוק מקרקעי ישראל"
                ]
            }
        }
        
        return category_info.get(category_id)