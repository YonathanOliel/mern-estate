import re
import logging
from typing import List, Dict, Optional, Tuple
from hebrew_tokenizer import tokenize

logger = logging.getLogger(__name__)

class HebrewProcessor:
    """
    מעבד טקסט עברי מתקדם
    מטפל בניקוי טקסט, תקינה לשונית, וזיהוי סלנג משפטי
    """
    
    def __init__(self):
        """אתחול המעבד עם מילונים וכללי עיבוד"""
        
        # Legal slang and informal terms mapping
        self.legal_slang_mapping = {
            # Employment related slang
            "פוטרו אותי": "פיטורין",
            "עפו עלי": "פיטורין לא חוקיים",
            "זרקו אותי": "פיטורין",
            "בעל העבודה": "מעסיק",
            "הבוס": "מעסיק",
            "המנהל": "מעסיק",
            "משכורת": "שכר",
            "מזומנים": "תשלום במזומן",
            
            # Rental related slang
            "בעל הבית": "משכיר",
            "בעלת הבית": "משכירה", 
            "דיירת": "שוכרת",
            "דייר": "שוכר",
            "ארנונה": "מס עירוני",
            "ועד בית": "ועד הבית",
            "חובה": "התחייבות",
            
            # Consumer related slang
            "קניתי": "רכישה",
            "החזר": "החזרת כסף",
            "אחריות": "שירות אחריות",
            "מוצר פגום": "מוצר לקוי",
            "לא עובד": "לקוי",
            
            # General legal slang
            "עורך דין": "יועץ משפטי",
            "עו\"ד": "עורך דין",
            "משפט": "הליך משפטי",
            "לתבוע": "להגיש תביעה",
            "תביעה": "הליך משפטי",
            "חוק": "חקיקה"
        }
        
        # Common Hebrew legal terms
        self.legal_terms = {
            "פיטורין", "שכר", "חוזה", "זכויות", "חובות", "תביעה",
            "משפט", "עורך דין", "הסכם", "ביטוח", "אחריות", "פיצוי",
            "נזק", "הפרה", "התחייבות", "ערבות", "משכיר", "שוכר",
            "מעסיק", "עובד", "צרכן", "ספק", "שירות", "מוצר"
        }
        
        # Hebrew text normalization patterns
        self.normalization_patterns = [
            # Fix common Hebrew typing mistakes
            (r'י{2,}', 'י'),  # Multiple yod
            (r'ו{2,}', 'ו'),  # Multiple vav
            (r'ה{2,}', 'ה'),  # Multiple he
            
            # Normalize punctuation
            (r'\.{2,}', '...'),  # Multiple dots
            (r'\?{2,}', '?'),    # Multiple question marks
            (r'!{2,}', '!'),     # Multiple exclamation marks
            
            # Remove extra whitespace
            (r'\s+', ' '),       # Multiple spaces
            (r'\n+', '\n'),      # Multiple newlines
        ]

    def process_text(self, text: str) -> str:
        """
        עיבוד מלא של טקסט עברי
        
        Args:
            text: הטקסט המקורי
            
        Returns:
            הטקסט המעובד והמנוקה
        """
        try:
            # Basic cleaning
            processed_text = self._clean_text(text)
            
            # Normalize Hebrew text
            processed_text = self._normalize_hebrew(processed_text)
            
            # Replace slang with formal terms
            processed_text = self._replace_slang(processed_text)
            
            # Enhance legal context
            processed_text = self._enhance_legal_context(processed_text)
            
            logger.debug(f"Text processed: '{text}' -> '{processed_text}'")
            return processed_text
            
        except Exception as e:
            logger.error(f"Error processing Hebrew text: {str(e)}")
            return text  # Return original text if processing fails

    def extract_legal_entities(self, text: str) -> Dict[str, List[str]]:
        """
        חילוץ ישויות משפטיות מהטקסט
        
        Returns:
            מילון עם סוגי ישויות ורשימת הישויות שנמצאו
        """
        entities = {
            "legal_terms": [],
            "monetary_amounts": [],
            "dates": [],
            "parties": [],
            "locations": []
        }
        
        try:
            # Extract legal terms
            words = text.split()
            for word in words:
                clean_word = re.sub(r'[^\u0590-\u05FF\w]', '', word)
                if clean_word in self.legal_terms:
                    entities["legal_terms"].append(clean_word)
            
            # Extract monetary amounts
            money_patterns = [
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:שקל|ש"ח|₪)',
                r'(\d+(?:,\d{3})*)\s*(?:אלף|מיליון)',
            ]
            
            for pattern in money_patterns:
                matches = re.findall(pattern, text)
                entities["monetary_amounts"].extend(matches)
            
            # Extract dates
            date_patterns = [
                r'\d{1,2}[./]\d{1,2}[./]\d{2,4}',  # DD/MM/YYYY or DD.MM.YYYY
                r'\d{1,2}\s+(?:ינואר|פברואר|מרץ|אפריל|מאי|יוני|יולי|אוגוסט|ספטמבר|אוקטובר|נובמבר|דצמבר)\s+\d{4}',
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text)
                entities["dates"].extend(matches)
                
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting legal entities: {str(e)}")
            return entities

    def detect_urgency_level(self, text: str) -> Tuple[str, float]:
        """
        זיהוי רמת דחיפות בטקסט
        
        Returns:
            טאפל של (רמת דחיפות, ציון דחיפות)
        """
        urgency_indicators = {
            "high": [
                "דחוף", "מיידי", "בהקדם", "חירום", "עכשיו", "מיד",
                "פיטורין מיידיים", "פינוי", "תביעה", "בית משפט",
                "הוצאה לפועל", "עיקול"
            ],
            "medium": [
                "בקרוב", "השבוע", "החודש", "בעיה", "צריך עזרה",
                "לא בסדר", "לא הוגן", "רוצה לפתור"
            ],
            "low": [
                "בעתיד", "כשיהיה זמן", "רק לדעת", "סתם שאלה",
                "סקרנות", "מידע כללי"
            ]
        }
        
        text_lower = text.lower()
        urgency_score = 0.0
        detected_level = "low"
        
        for level, indicators in urgency_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    if level == "high":
                        urgency_score += 3.0
                        detected_level = "high"
                    elif level == "medium":
                        urgency_score += 2.0
                        if detected_level == "low":
                            detected_level = "medium"
                    else:
                        urgency_score += 1.0
        
        # Normalize score to 0-1 range
        normalized_score = min(urgency_score / 10.0, 1.0)
        
        return detected_level, normalized_score

    def _clean_text(self, text: str) -> str:
        """ניקוי בסיסי של הטקסט"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere
        text = re.sub(r'[^\u0590-\u05FF\w\s\.,!?\-()"]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text

    def _normalize_hebrew(self, text: str) -> str:
        """תקינה של טקסט עברי"""
        for pattern, replacement in self.normalization_patterns:
            text = re.sub(pattern, replacement, text)
        
        return text

    def _replace_slang(self, text: str) -> str:
        """החלפת סלנג במונחים פורמליים"""
        for slang, formal in self.legal_slang_mapping.items():
            # Case-insensitive replacement for Hebrew
            pattern = re.compile(re.escape(slang), re.IGNORECASE)
            text = pattern.sub(formal, text)
        
        return text

    def _enhance_legal_context(self, text: str) -> str:
        """הוספת הקשר משפטי לטקסט"""
        # Add context markers for better AI understanding
        enhanced_text = text
        
        # Add category hints based on content
        if any(term in text.lower() for term in ["פיטורין", "עבודה", "מעסיק", "שכר"]):
            enhanced_text = f"[הקשר: דיני עבודה] {enhanced_text}"
        elif any(term in text.lower() for term in ["שכירות", "דירה", "בעל בית", "דייר"]):
            enhanced_text = f"[הקשר: דיני שכירות] {enhanced_text}"
        elif any(term in text.lower() for term in ["קנייה", "מוצר", "חנות", "צרכן"]):
            enhanced_text = f"[הקשר: דיני צרכנות] {enhanced_text}"
        elif any(term in text.lower() for term in ["נישואין", "גירושין", "ילדים", "משפחה"]):
            enhanced_text = f"[הקשר: דיני משפחה] {enhanced_text}"
        
        return enhanced_text

    def tokenize_hebrew(self, text: str) -> List[str]:
        """פיצול טקסט עברי לטוקנים"""
        try:
            tokens = tokenize(text)
            return [token[0] for token in tokens if token[0].strip()]
        except Exception as e:
            logger.error(f"Error tokenizing Hebrew text: {str(e)}")
            # Fallback to simple word splitting
            return text.split()

    def is_hebrew_text(self, text: str) -> bool:
        """בדיקה האם הטקסט מכיל עברית"""
        hebrew_chars = re.findall(r'[\u0590-\u05FF]', text)
        total_chars = len(re.findall(r'[a-zA-Z\u0590-\u05FF]', text))
        
        if total_chars == 0:
            return False
            
        hebrew_ratio = len(hebrew_chars) / total_chars
        return hebrew_ratio > 0.5  # More than 50% Hebrew characters