"""
License Key Generator
برنامج توليد مفاتيح التفعيل (للمطورين فقط)
"""

import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox,
    QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from core.hwid import HWIDGenerator
from core.license_manager import LicenseManager
from ui.theme_engine import ThemeEngine
from ui.animated_button import AnimatedButton


class KeyGeneratorWindow(QMainWindow):
    """نافذة توليد مفاتيح التفعيل"""
    
    def __init__(self):
        """تهيئة النافذة"""
        super().__init__()
        self.theme_engine = ThemeEngine("dark")
        
        self.setWindowTitle("🔑 مولد مفاتيح التفعيل - SmartFileRenamer")
        self.setGeometry(100, 100, 700, 600)
        self.setStyleSheet(self.theme_engine.get_stylesheet())
        
        self.setup_ui()
    
    def setup_ui(self):
        """بناء واجهة النافذة"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # الرأس
        header = QLabel("🔐 مولد مفاتيح التفعيل - SmartFileRenamer")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        main_layout.addWidget(header)
        
        # تحذير
        warning = QLabel("⚠️ هذا البرنامج للمطورين فقط - استخدمه لتوليد مفاتيح الاختبار")
        warning.setFont(QFont("Arial", 10))
        warning.setStyleSheet(f"color: {self.theme_engine.get_color('warning')};")
        main_layout.addWidget(warning)
        
        # قسم إدخال HWID
        main_layout.addWidget(QLabel("📱 معرف الجهاز (HWID):"))
        
        hwid_input_layout = QHBoxLayout()
        self.hwid_input = QLineEdit()
        self.hwid_input.setPlaceholderText("أدخل HWID أو اترك فارغاً للتوليد التلقائي")
        hwid_input_layout.addWidget(self.hwid_input)
        
        generate_hwid_btn = AnimatedButton("🔄 توليد HWID")
        generate_hwid_btn.clicked.connect(self.generate_hwid)
        hwid_input_layout.addWidget(generate_hwid_btn)
        
        main_layout.addLayout(hwid_input_layout)
        
        # قسم صلاحية المفتاح
        validity_layout = QHBoxLayout()
        validity_layout.addWidget(QLabel("📅 صلاحية المفتاح (أيام):"))
        
        self.validity_spin = QSpinBox()
        self.validity_spin.setMinimum(1)
        self.validity_spin.setMaximum(3650)
        self.validity_spin.setValue(365)
        validity_layout.addWidget(self.validity_spin)
        validity_layout.addStretch()
        
        main_layout.addLayout(validity_layout)
        
        # قسم توليد المفتاح
        generate_layout = QHBoxLayout()
        
        self.generate_key_btn = AnimatedButton("✨ توليد مفتاح جديد")
        self.generate_key_btn.clicked.connect(self.generate_key)
        generate_layout.addWidget(self.generate_key_btn)
        
        self.copy_key_btn = AnimatedButton("📋 نسخ المفتاح")
        self.copy_key_btn.clicked.connect(self.copy_key)
        self.copy_key_btn.setEnabled(False)
        generate_layout.addWidget(self.copy_key_btn)
        
        main_layout.addLayout(generate_layout)
        
        # عرض المفتاح
        main_layout.addWidget(QLabel("🔑 المفتاح المولد:"))
        
        self.key_display = QTextEdit()
        self.key_display.setReadOnly(True)
        self.key_display.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        self.key_display.setMinimumHeight(60)
        main_layout.addWidget(self.key_display)
        
        # عرض البيانات الوصفية
        main_layout.addWidget(QLabel("📊 البيانات الوصفية:"))
        
        self.metadata_display = QTextEdit()
        self.metadata_display.setReadOnly(True)
        self.metadata_display.setFont(QFont("Courier New", 9))
        self.metadata_display.setMinimumHeight(150)
        main_layout.addWidget(self.metadata_display)
        
        # أزرار التحكم
        action_layout = QHBoxLayout()
        
        self.save_btn = AnimatedButton("💾 حفظ المفتاح")
        self.save_btn.clicked.connect(self.save_key)
        self.save_btn.setEnabled(False)
        action_layout.addWidget(self.save_btn)
        
        self.verify_btn = AnimatedButton("✅ التحقق من المفتاح")
        self.verify_btn.clicked.connect(self.verify_key)
        action_layout.addWidget(self.verify_btn)
        
        clear_btn = AnimatedButton("🗑️ مسح")
        clear_btn.clicked.connect(self.clear_all)
        action_layout.addWidget(clear_btn)
        
        main_layout.addLayout(action_layout)
        
        # معلومات إضافية
        info = QLabel("💡 نصيحة: يمكنك حفظ المفاتيح لإرسالها للعملاء")
        info.setFont(QFont("Arial", 9))
        info.setStyleSheet(f"color: {self.theme_engine.get_color('secondary_text')};")
        main_layout.addWidget(info)
        
        self.current_hwid = None
        self.current_key = None
        self.current_metadata = None
    
    def generate_hwid(self):
        """توليد HWID جديد"""
        hwid, components = HWIDGenerator.generate_hwid()
        self.hwid_input.setText(hwid)
        self.current_hwid = hwid
        
        QMessageBox.information(
            self,
            "✅ تم التوليد",
            f"تم توليد HWID:\n\n{hwid}\n\n{json.dumps(components, indent=2, ensure_ascii=False)}"
        )
    
    def generate_key(self):
        """توليد مف��اح تفعيل جديد"""
        hwid = self.hwid_input.text().strip()
        
        if not hwid:
            QMessageBox.warning(
                self,
                "⚠️ تحذير",
                "الرجاء إدخال HWID أو توليد واحد جديد"
            )
            return
        
        try:
            days = self.validity_spin.value()
            serial, metadata = LicenseManager.generate_serial(hwid, days)
            
            self.current_key = serial
            self.current_metadata = metadata
            self.current_hwid = hwid
            
            # عرض المفتاح
            self.key_display.setText(serial)
            
            # عرض البيانات الوصفية
            metadata_text = json.dumps(metadata, indent=2, ensure_ascii=False)
            self.metadata_display.setText(metadata_text)
            
            # تفعيل الأزرار
            self.copy_key_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            
            self.statusBar().showMessage("✅ تم توليد المفتاح بنجاح")
        
        except Exception as e:
            QMessageBox.critical(self, "❌ خطأ", f"خطأ في التوليد:\n{str(e)}")
    
    def copy_key(self):
        """نسخ المفتاح إلى الحافظة"""
        if not self.current_key:
            return
        
        from PyQt6.QtGui import QClipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(self.current_key)
        
        self.statusBar().showMessage("✅ تم نسخ المفتاح إلى الحافظة")
    
    def save_key(self):
        """حفظ المفتاح في ملف"""
        if not self.current_key or not self.current_metadata:
            return
        
        try:
            key_data = {
                "serial": self.current_key,
                "hwid": self.current_hwid,
                "metadata": self.current_metadata
            }
            
            filename = f"license_key_{self.current_hwid[:8]}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(key_data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(
                self,
                "✅ تم الحفظ",
                f"تم حفظ المفتاح في:\n{filename}"
            )
            
            self.statusBar().showMessage(f"✅ تم حفظ المفتاح: {filename}")
        
        except Exception as e:
            QMessageBox.critical(self, "❌ خطأ", f"خطأ في الحفظ:\n{str(e)}")
    
    def verify_key(self):
        """التحقق من المفتاح"""
        if not self.current_key or not self.current_hwid:
            QMessageBox.warning(
                self,
                "⚠️ تحذير",
                "الرجاء توليد مفتاح أولاً"
            )
            return
        
        is_valid, metadata = LicenseManager.verify_serial(
            self.current_key,
            self.current_hwid
        )
        
        if is_valid:
            QMessageBox.information(
                self,
                "✅ المفتاح صحيح",
                f"المفتاح سليم ويمكن استخدامه:\n\n{self.current_key}"
            )
        else:
            QMessageBox.critical(
                self,
                "❌ المفتاح غير صحيح",
                "فشل التحقق من صحة المفتاح"
            )
    
    def clear_all(self):
        """مسح جميع الحقول"""
        self.hwid_input.clear()
        self.key_display.clear()
        self.metadata_display.clear()
        self.validity_spin.setValue(365)
        
        self.copy_key_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        
        self.current_hwid = None
        self.current_key = None
        self.current_metadata = None
        
        self.statusBar().showMessage("✅ تم مسح جميع الحقول")


def main():
    """نقطة الدخول"""
    app = QApplication(sys.argv)
    window = KeyGeneratorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
