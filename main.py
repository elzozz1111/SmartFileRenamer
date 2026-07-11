"""
SmartFileRenamer - Main Application
تطبيق إعادة تسمية الملفات الذكي

الميزات:
- محرك إعادة تسمية ذكي بالذكاء الاصطناعي
- نظام تفعيل آمن بـ HWID
- واجهة رسومية حديثة مع ثيمات
- قاعدة بيانات مع undo/redo
- عمليات خلفية بسلاسة
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from ui.theme_engine import ThemeEngine
from ui.activation_window import ActivationWindow
from ui.main_window import MainWindow
from core.license_manager import LicenseManager
from core.hwid import HWIDGenerator


def check_activation():
    """
    التحقق من تفعيل البرنامج
    إذا لم يتم التفعيل، عرض نافذة التفعيل
    """
    if LicenseManager.is_license_valid():
        print("✅ البرنامج مفعل بنجاح")
        return True
    
    print("⚠️ البرنامج غير مفعل")
    return False


def main():
    """نقطة دخول التطبيق"""
    
    # إنشاء التطبيق
    app = QApplication(sys.argv)
    
    # تهيئة محرك الثيمات
    theme_engine = ThemeEngine("dark")
    
    # التحقق من التفعيل
    if not check_activation():
        # عرض نافذة التفعيل
        activation_window = ActivationWindow(theme_engine)
        
        # إذا لم يتم التفعيل، إغلاق البرنامج
        if activation_window.exec() != ActivationWindow.DialogCode.Accepted:
            print("❌ تم إغلاق البرنامج بدون تفعيل")
            sys.exit(1)
    
    # عرض النافذة الرئيسية
    main_window = MainWindow(theme_engine)
    main_window.show()
    
    # تشغيل البرنامج
    print("🚀 تم بدء التطبيق")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
