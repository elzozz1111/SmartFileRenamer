"""
AI Renaming Engine Module
محرك إعادة التسمية الذكي باستخدام OpenAI API
"""

import os
from typing import List, Dict, Optional
from pathlib import Path


class AIEngine:
    """محرك إعادة التسمية الذكي"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        تهيئة محرك الذكاء الاصطناعي
        
        Args:
            api_key: مفتاح OpenAI API (اختياري)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("⚠️ مكتبة OpenAI غير مثبتة")
    
    def generate_name_suggestions(self, current_name: str, 
                                 context: str = "") -> List[str]:
        """
        توليد اقتراحات أسماء ذكية
        
        Args:
            current_name: الاسم الحالي للملف
            context: سياق إضافي (مثل نوع المجلد)
        
        Returns:
            قائمة بالاقتراحات
        """
        
        # إذا لم يكن هناك API key، استخدم قواعد محلية
        if not self.client:
            return self._generate_local_suggestions(current_name, context)
        
        try:
            # إنشاء prompt ذكي
            prompt = self._create_prompt(current_name, context)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "أنت مساعد متخصص في إعادة تسمية الملفات بطريقة ذكية واحترافية."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            # استخراج الاقتراحات من الرد
            suggestions = self._parse_suggestions(response.choices[0].message.content)
            return suggestions
        
        except Exception as e:
            print(f"⚠️ خطأ في استدعاء AI: {e}")
            return self._generate_local_suggestions(current_name, context)
    
    def _create_prompt(self, current_name: str, context: str) -> str:
        """إنشاء prompt مخصص"""
        prompt = f"""
        اقترح 5 أسماء احترافية جديدة للملف التالي:
        الاسم الحالي: {current_name}
        """
        
        if context:
            prompt += f"\nالسياق: {context}"
        
        prompt += """
        
        المتطلبات:
        - الأسماء يجب أن تكون واضحة وموجزة
        - تجنب الأسماء المعقدة
        - استخدم underscore أو hyphen بدل المسافات
        - اجعل الأسماء وصفية
        
        أرجع الأسماء في صيغة قائمة مرقمة بسيطة.
        """
        
        return prompt
    
    def _parse_suggestions(self, response_text: str) -> List[str]:
        """استخراج الاقتراحات من رد AI"""
        suggestions = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # إزالة الترقيم والعلامات
            for char in ['1', '2', '3', '4', '5', '.', '-', '*', '']:
                line = line.replace(char, '', 1).strip()
            
            if line and len(line) > 3:
                suggestions.append(line)
        
        return suggestions[:5]  # إرجاع أول 5 اقتراحات
    
    def _generate_local_suggestions(self, current_name: str, 
                                   context: str = "") -> List[str]:
        """توليد اقتراحات بدون اتصال إنترنت"""
        file_ext = Path(current_name).suffix
        file_stem = Path(current_name).stem
        
        suggestions = []
        
        # اقتراح 1: إزالة الأرقام والرموز الخاصة
        clean_name = "".join(c if c.isalnum() or c in ' _-' else '' 
                            for c in file_stem).strip()
        if clean_name and clean_name != file_stem:
            suggestions.append(f"{clean_name}{file_ext}")
        
        # اقتراح 2: تحويل إلى camelCase
        words = file_stem.split('_')
        camel_case = words[0].lower() + "".join(w.capitalize() for w in words[1:])
        if camel_case and camel_case != file_stem:
            suggestions.append(f"{camel_case}{file_ext}")
        
        # اقتراح 3: تحويل إلى snake_case
        snake_case = "_".join(file_stem.split())
        if snake_case and snake_case != file_stem:
            suggestions.append(f"{snake_case}{file_ext}")
        
        # اقتراح 4: إضافة تاريخ/وقت
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d")
        suggestions.append(f"{file_stem}_{timestamp}{file_ext}")
        
        # اقتراح 5: إضافة رقم تسلسلي
        suggestions.append(f"{file_stem}_v1{file_ext}")
        
        return suggestions[:5]
    
    def batch_rename_suggestions(self, file_paths: List[str], 
                                context: str = "") -> Dict[str, List[str]]:
        """توليد اقتراحات لعدة ملفات"""
        suggestions = {}
        
        for file_path in file_paths:
            try:
                file_name = Path(file_path).name
                suggestions[file_path] = self.generate_name_suggestions(
                    file_name, context
                )
            except Exception as e:
                print(f"⚠️ خطأ في معالجة {file_path}: {e}")
                suggestions[file_path] = []
        
        return suggestions
