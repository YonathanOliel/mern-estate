import os
import openai
from typing import Dict, List, Optional, Any
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LegalAI:
    """
    מודול הבינה המלאכותית המשפטית הראשי
    מתמחה בהבנת בקשות משפטיות בעברית ויצירת תגובות מותאמות
    """
    
    def __init__(self):
        """אתחול המודול עם הגדרות OpenAI"""
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '4096'))
        
        # Legal system prompts in Hebrew
        self.system_prompts = {
            "general": """אתה עורך דין ישראלי מומחה וידידותי. תפקידך לעזור לאנשים בבעיות משפטיות באופן נגיש, ברור ומקצועי.

כללי התנהגות:
1. תמיד תענה בעברית ברורה ופשוטה
2. הסבר מושגים משפטיים באופן נגיש
3. הצע פתרונות מעשיים וצעדים קונקרטיים
4. אם המצב מורכב, המלץ על פנייה לעורך דין
5. תמיד הדגש שזה ייעוץ כללי ולא ייעוץ משפטי פורמלי
6. היה אמפתי ותומך

זכור: אתה כאן כדי להנגיש את החוק לקהל הרחב.""",

            "employment": """אתה מתמחה בדיני עבודה ישראליים. אתה מכיר היטב את:
- חוק הגנת השכר
- חוק שעות עבודה ומנוחה  
- חוק פיצויי פיטורין
- חוק שכר שווה
- חוק הודעה מוקדמת לפיטורין

תמיד הסבר את הזכויות בצורה ברורה ותן דוגמאות מעשיות.""",

            "rental": """אתה מתמחה בדיני שכירות ישראליים. אתה מכיר:
- חוק הגנת הדייר
- דיני שכירות מסחרית
- זכויות ושכירות
- הליכי פינוי
- תיקוני חוזים

הסבר את הזכויות והחובות של שוכר ומשכיר בבירור.""",

            "consumer": """אתה מתמחה בדיני צרכנות ישראליים:
- חוק הגנת הצרכן
- זכויות החזרה וביטול עסקה
- אחריות על מוצרים
- פרסום מטעה
- תביעות קטנות

תן דגש על הזכויות המעשיות של הצרכן."""
        }

    async def generate_response(
        self, 
        message: str, 
        category: Optional[str] = None,
        context: Dict[str, Any] = {},
        language: str = "hebrew"
    ) -> Dict[str, Any]:
        """
        יצירת תגובה מותאמת לבקשה המשפטית
        
        Args:
            message: ההודעה מהמשתמש
            category: הקטגוריה המשפטית שזוהתה
            context: הקשר נוסף מהשיחה
            language: שפת התגובה
        
        Returns:
            מילון עם התגובה ומידע נוסף
        """
        try:
            # Choose appropriate system prompt
            system_prompt = self.system_prompts.get(category, self.system_prompts["general"])
            
            # Build conversation context
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history if exists
            if context.get("conversation_history"):
                for msg in context["conversation_history"][-5:]:  # Last 5 messages
                    messages.append(msg)
            
            # Add current message
            messages.append({
                "role": "user", 
                "content": f"קטגוריה משפטית: {category}\nשאלה: {message}"
            })
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.3,  # Lower temperature for more consistent legal advice
                top_p=0.9
            )
            
            response_text = response.choices[0].message.content
            
            # Analyze response quality
            confidence = await self._calculate_confidence(message, response_text, category)
            requires_clarification = await self._needs_clarification(message, response_text)
            
            return {
                "text": response_text,
                "confidence": confidence,
                "requires_clarification": requires_clarification,
                "category": category,
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return {
                "text": "מצטער, אירעה שגיאה בעיבוד הבקשה. אנא נסה שוב.",
                "confidence": 0.0,
                "requires_clarification": True,
                "error": str(e)
            }

    async def generate_follow_up_questions(
        self, 
        message: str, 
        category: Optional[str] = None,
        language: str = "hebrew"
    ) -> List[str]:
        """יצירת שאלות המשך מותאמות לקטגוריה המשפטית"""
        
        category_questions = {
            "employment": [
                "כמה זמן עבדת במקום העבודה?",
                "האם קיבלת הודעה מוקדמת על הפיטורין?",
                "האם יש לך חוזה עבודה כתוב?",
                "מה הסיבה שניתנה לפיטורין?"
            ],
            "rental": [
                "האם יש לך חוזה שכירות כתוב?",
                "כמה זמן אתה שוכר את הנכס?",
                "מה סכום השכירות החודשית?",
                "האם שילמת פיקדון?"
            ],
            "consumer": [
                "מתי רכשת את המוצר/השירות?",
                "האם יש לך קבלה או חשבונית?",
                "מה בדיוק הבעיה עם המוצר?",
                "האם פנית כבר לחברה?"
            ],
            "family": [
                "האם אתם נשואים או ידועים בציבור?",
                "האם יש ילדים משותפים?",
                "האם יש רכוש משותף?",
                "האם ניסיתם גישור?"
            ]
        }
        
        return category_questions.get(category, [
            "אפשר לספר עוד פרטים על המצב?",
            "מתי זה קרה?",
            "איך תרצה להמשיך?",
            "האם יש מסמכים רלוונטיים?"
        ])

    async def suggest_next_steps(
        self, 
        category: Optional[str] = None,
        context: Dict[str, Any] = {}
    ) -> List[str]:
        """הצעת צעדים הבאים בהתאם לקטגוריה המשפטית"""
        
        category_steps = {
            "employment": [
                "איסוף כל המסמכים הרלוונטיים (חוזה עבודה, תלושי שכר)",
                "חישוב הזכויות (פיצויי פיטורין, הודעה מוקדמת, חופשה)",
                "פנייה למעסיק בכתב לדרישת התשלומים",
                "במידת הצורך - הגשת תביעה לבית הדין לעבודה"
            ],
            "rental": [
                "בדיקת תנאי החוזה",
                "תיעוד הבעיה בכתב ובתמונות",
                "פנייה למשכיר/לשוכר בכתב",
                "במידת הצורך - פנייה לבית משפט השלום"
            ],
            "consumer": [
                "פנייה לחברה בכתב עם דרישה לתיקון/החזרה",
                "שמירת כל המסמכים והתכתובות",
                "פנייה למוקד הצרכנות של משרד הכלכלה",
                "במידת הצורך - תביעה קטנה"
            ]
        }
        
        return category_steps.get(category, [
            "איסוף מידע ומסמכים רלוונטיים",
            "בירור הזכויות החוקיות",
            "ניסיון פתרון בדרכי שלום",
            "התייעצות עם עורך דין מוסמך"
        ])

    async def get_category_starter(self, category: str) -> Dict[str, Any]:
        """קבלת הודעת פתיחה ושאלות התחלתיות לקטגוריה"""
        
        starters = {
            "employment": {
                "welcome_message": "היי! אני כאן לעזור לך בנושאי דיני עבודה. בואו נבין יחד מה המצב ומה הזכויות שלך.",
                "initial_questions": [
                    "פוטרת מהעבודה ולא ברור לי מה מגיע לי",
                    "יש לי בעיה עם המעסיק שלי",
                    "רוצה לדעת על זכויות עובדים",
                    "צריך לכתוב מכתב התראה למעסיק"
                ],
                "next_steps": ["ספר לי מה קרה", "איסוף פרטים על המצב", "בדיקת זכויות"]
            },
            "rental": {
                "welcome_message": "שלום! אני כאן לעזור לך בנושאי שכירות ונדל\"ן. בואו נפתור יחד את הבעיה.",
                "initial_questions": [
                    "בעיות עם בעל הבית/השוכר",
                    "רוצה לכתוב חוזה שכירות",
                    "בעיות תחזוקה בדירה",
                    "שאלות על פיקדון ושכירות"
                ],
                "next_steps": ["תיאור המצב", "בדיקת החוזה", "הבנת הזכויות"]
            },
            "consumer": {
                "welcome_message": "ברוכים הבאים! אני כאן לעזור לך בזכויות צרכן. בואו נדאג שתקבל את מה שמגיע לך.",
                "initial_questions": [
                    "קניתי משהו ויש בעיה",
                    "רוצה להחזיר מוצר",
                    "חברה לא מכבדת אחריות",
                    "בעיות עם שירות לקוחות"
                ],
                "next_steps": ["פרטים על הרכישה", "תיאור הבעיה", "בדיקת זכויות החזרה"]
            }
        }
        
        return starters.get(category, {
            "welcome_message": "שלום! אני כאן לעזור לך בנושאים משפטיים. איך אוכל לסייע?",
            "initial_questions": [
                "יש לי בעיה משפטית",
                "צריך עזרה עם מסמך",
                "רוצה לדעת על זכויות",
                "צריך ייעוץ משפטי"
            ],
            "next_steps": ["תיאור הבעיה", "בירור הפרטים", "הבנת הזכויות"]
        })

    async def _calculate_confidence(self, question: str, response: str, category: str) -> float:
        """חישוב רמת הביטחון בתגובה"""
        # Simple confidence calculation - can be enhanced with ML models
        confidence = 0.7  # Base confidence
        
        # Adjust based on category match
        if category and category != "unknown":
            confidence += 0.2
        
        # Adjust based on response length and structure
        if len(response) > 100 and "זכויות" in response:
            confidence += 0.1
            
        return min(confidence, 1.0)

    async def _needs_clarification(self, question: str, response: str) -> bool:
        """בדיקה האם נדרשת הבהרה נוספת"""
        clarification_indicators = [
            "פרטים נוספים",
            "מידע נוסף", 
            "לא ברור",
            "תלוי במקרה",
            "צריך לבדוק"
        ]
        
        return any(indicator in response for indicator in clarification_indicators)