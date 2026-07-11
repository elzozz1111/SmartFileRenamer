"""
Workers Module
عمليات خلفية لإعادة التسمية والنسخ
"""

import os
import shutil
from pathlib import Path
from typing import Callable, Optional, Dict, List
from PyQt6.QtCore import QThread, pyqtSignal, QObject


class RenameWorker(QThread):
    """عامل إعادة التسمية الخلفي"""
    
    # الإشارات
    progress = pyqtSignal(int)  # النسبة المئوية
    status = pyqtSignal(str)  # رسالة الحالة
    finished = pyqtSignal(bool)  # انتهت العملية
    error = pyqtSignal(str)  # رسالة الخطأ
    
    def __init__(self, rename_map: Dict[str, str], db_manager=None):
        """
        تهيئة عامل إعادة التسمية
        
        Args:
            rename_map: قاموس {المسار_القديم: المسار_الجديد}
            db_manager: مدير قاعدة البيانات
        """
        super().__init__()
        self.rename_map = rename_map
        self.db_manager = db_manager
        self.is_running = True
    
    def run(self):
        """تنفيذ العملية"""
        try:
            total_files = len(self.rename_map)
            completed = 0
            
            for old_path, new_path in self.rename_map.items():
                if not self.is_running:
                    break
                
                try:
                    old_path_obj = Path(old_path)
                    new_path_obj = Path(new_path)
                    
                    # التحقق من وجود الملف القديم
                    if not old_path_obj.exists():
                        self.status.emit(f"⚠️ الملف غير موجود: {old_path}")
                        completed += 1
                        continue
                    
                    # التحقق من عدم وجود الملف الجديد
                    if new_path_obj.exists():
                        self.error.emit(f"❌ الملف موجود بالفعل: {new_path}")
                        completed += 1
                        continue
                    
                    # إعادة التسمية
                    old_path_obj.rename(new_path_obj)
                    
                    # حفظ في قاعدة البيانات
                    if self.db_manager:
                        file_size = new_path_obj.stat().st_size
                        self.db_manager.add_rename_record(
                            old_path_obj.name,
                            new_path_obj.name,
                            str(new_path_obj),
                            file_size
                        )
                    
                    self.status.emit(f"✅ تم إعادة تسمية: {old_path_obj.name} → {new_path_obj.name}")
                    
                except Exception as e:
                    self.error.emit(f"❌ خطأ: {str(e)}")
                
                finally:
                    completed += 1
                    progress_percent = int((completed / total_files) * 100)
                    self.progress.emit(progress_percent)
            
            self.finished.emit(True)
        
        except Exception as e:
            self.error.emit(f"❌ خطأ عام: {str(e)}")
            self.finished.emit(False)
    
    def stop(self):
        """إيقاف العملية"""
        self.is_running = False


class CopyWorker(QThread):
    """عامل النسخ الخلفي"""
    
    # الإشارات
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)
    
    def __init__(self, source_files: List[str], destination: str):
        """
        تهيئة عامل النسخ
        
        Args:
            source_files: قائمة الملفات المراد نسخها
            destination: مسار الوجهة
        """
        super().__init__()
        self.source_files = source_files
        self.destination = destination
        self.is_running = True
    
    def run(self):
        """تنفيذ العملية"""
        try:
            dest_path = Path(self.destination)
            dest_path.mkdir(parents=True, exist_ok=True)
            
            total_files = len(self.source_files)
            completed = 0
            total_size = 0
            copied_size = 0
            
            # حساب الحجم الإجمالي
            for file_path in self.source_files:
                try:
                    total_size += Path(file_path).stat().st_size
                except:
                    pass
            
            # نسخ الملفات
            for source_file in self.source_files:
                if not self.is_running:
                    break
                
                try:
                    source_path = Path(source_file)
                    
                    if not source_path.exists():
                        self.status.emit(f"⚠️ الملف غير موجود: {source_file}")
                        completed += 1
                        continue
                    
                    dest_file = dest_path / source_path.name
                    
                    # نسخ الملف
                    shutil.copy2(source_file, dest_file)
                    copied_size += source_path.stat().st_size
                    
                    self.status.emit(f"✅ تم نسخ: {source_path.name}")
                    
                except Exception as e:
                    self.error.emit(f"❌ خطأ في النسخ: {str(e)}")
                
                finally:
                    completed += 1
                    if total_size > 0:
                        progress_percent = int((copied_size / total_size) * 100)
                    else:
                        progress_percent = int((completed / total_files) * 100)
                    self.progress.emit(progress_percent)
            
            self.finished.emit(True)
        
        except Exception as e:
            self.error.emit(f"❌ خطأ عام: {str(e)}")
            self.finished.emit(False)
    
    def stop(self):
        """إيقاف العملية"""
        self.is_running = False
