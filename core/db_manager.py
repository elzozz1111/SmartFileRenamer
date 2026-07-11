"""
Database Manager Module
إدارة قاعدة بيانات SQLite مع دعم Undo/Redo
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class DatabaseManager:
    """إدارة قاعدة البيانات"""
    
    def __init__(self, db_path: str = "smartrename.db"):
        """تهيئة قاعدة البيانات"""
        self.db_path = db_path
        self.connection = None
        self.init_database()
    
    def init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            
            # جدول العمليات (Rename History)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rename_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    old_name TEXT NOT NULL,
                    new_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    operation_type TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'completed'
                )
            """)
            
            # جدول التراجع/الإعادة (Undo/Redo Stack)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS undo_redo_stack (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type TEXT NOT NULL,
                    old_data TEXT NOT NULL,
                    new_data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_redo BOOLEAN DEFAULT 0
                )
            """)
            
            # جدول الإعدادات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول الملفات المراقبة
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watched_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    last_modified DATETIME,
                    status TEXT DEFAULT 'active',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()
            print("✅ قاعدة البيانات جاهزة")
        
        except sqlite3.Error as e:
            print(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
    
    def add_rename_record(self, old_name: str, new_name: str, 
                         file_path: str, file_size: int = 0) -> bool:
        """إضافة سجل إعادة تسمية"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO rename_history 
                (old_name, new_name, file_path, file_size, operation_type)
                VALUES (?, ?, ?, ?, ?)
            """, (old_name, new_name, file_path, file_size, 'rename'))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ خطأ في إضافة السجل: {e}")
            return False
    
    def get_rename_history(self, limit: int = 100) -> List[Dict]:
        """الحصول على سجل العمليات"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM rename_history 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ خطأ في قراءة السجل: {e}")
            return []
    
    def push_undo_action(self, action_type: str, old_data: str, new_data: str) -> bool:
        """إضافة عملية للتراجع"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO undo_redo_stack 
                (action_type, old_data, new_data, is_redo)
                VALUES (?, ?, ?, 0)
            """, (action_type, old_data, new_data))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ خطأ في إضافة عملية التراجع: {e}")
            return False
    
    def get_undo_stack(self, limit: int = 50) -> List[Dict]:
        """الحصول على stack التراجع"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM undo_redo_stack 
                WHERE is_redo = 0
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ خطأ في قراءة stack التراجع: {e}")
            return []
    
    def clear_redo_stack(self) -> bool:
        """مسح stack الإعادة عند تنفيذ عملية جديدة"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM undo_redo_stack WHERE is_redo = 1")
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ خطأ في مسح stack الإعادة: {e}")
            return False
    
    def set_setting(self, key: str, value: str) -> bool:
        """حفظ إعداد"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
            """, (key, value))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ خطأ في حفظ الإعداد: {e}")
            return False
    
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """الحصول على إعداد"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default
        except sqlite3.Error as e:
            print(f"❌ خطأ في قراءة الإعداد: {e}")
            return default
    
    def get_statistics(self) -> Dict:
        """الحصول على إحصائيات العمليات"""
        try:
            cursor = self.connection.cursor()
            
            # عدد العمليات
            cursor.execute("SELECT COUNT(*) FROM rename_history")
            total_renames = cursor.fetchone()[0]
            
            # إجمالي الملفات المعاد تسميتها اليوم
            cursor.execute("""
                SELECT COUNT(*) FROM rename_history 
                WHERE DATE(timestamp) = DATE('now')
            """)
            today_renames = cursor.fetchone()[0]
            
            return {
                "total_renames": total_renames,
                "today_renames": today_renames,
                "database_file": self.db_path
            }
        except sqlite3.Error as e:
            print(f"❌ خطأ في الحصول على الإحصائيات: {e}")
            return {}
    
    def close(self):
        """إغلاق الاتصال"""
        if self.connection:
            self.connection.close()
    
    def __del__(self):
        """تنظيف عند حذف الكائن"""
        self.close()
