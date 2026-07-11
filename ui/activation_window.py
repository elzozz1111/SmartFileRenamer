"""
Activation Window
نافذة تفعيل البرنامج
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap
from ui.animated_button import AnimatedButton
from ui.theme_engine import ThemeEngine
from core.hwid import HWIDGenerator
from core.license_manager import LicenseManager
from pathlib import Path


class ActivationWindow(QDialog):
    """نافذة التفعيل"""
    
    activation_success = pyqtSignal()
    
    def __init__(self, theme_engine: ThemeEngine):
        """تهيئة النافذة"""
        super().__init__()
        self.theme_engine = theme_engine
        self.setWindowTitle("تفعيل البرنامج 🔐")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet(theme_engine.get_stylesheet())
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        """بناء واجهة النافذة"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # العنوان
        title = QLabel("🔐 تفعيل SmartFileRenamer")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # معرف الجهاز (HWID)
        hwid_label = QLabel("معرف الجهاز (HWID):")
        hwid_label.setFont(QFont("Arial", 11))
        layout.addWidget(hwid_label)
        
        self.hwid_input = QLineEdit()
        hwid, _ = HWIDGenerator.generate_hwid()
        self.hwid_input.setText(hwid)
        self.hwid_input.setReadOnly(True)
        layout.addWidget(self.hwid_input)
        
        # مفتاح التفعيل
        serial_label = QLabel("مفتاح التفعيل (Serial Key):")
        serial_label.setFont(QFont("Arial", 11))
        layout.addWidget(serial_label)
        
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("SFR-XXXXXXXX-XXXXXXXX")
        layout.addWidget(self.serial_input)
        
        # رسالة معلومات
        info_label = QLabel("📧 أدخل مفتاح التفعيل الذي تلقيته عبر البريد الإلكتروني")
        info_label.setFont(QFont("Arial", 9))
        info_label.setStyleSheet(f"color: {self.theme_engine.get_color('secondary_text')};")
        layout.addWidget(info_label)
        
        # أزرار
        button_layout = QHBoxLayout()
        
        self.activate_btn = AnimatedButton("✅ تفعيل الآن")
        self.activate_btn.clicked.connect(self.activate)
        button_layout.addWidget(self.activate_btn)
        
        self.exit_btn = AnimatedButton("❌ خروج")
        self.exit_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.exit_btn)
        
        layout.addLayout(button_layout)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
    
    def activate(self):
        """تفعيل البرنامج"""
        serial = self.serial_input.text().strip()
        hwid = self.hwid_input.text().strip()
        
        if not serial:
            QMessageBox.warning(self, "⚠️ تحذير", "الرجاء إدخال مفتاح التفعيل")
            return
        
        # عرض شريط التقدم
        self.progress_bar.setVisible(True)
        self.activate_btn.setEnabled(False)
        
        # محاكاة التحقق
        for i in range(0, 101, 10):
            self.progress_bar.setValue(i)
            QTimer.singleShot(i * 10, lambda: None)
        
        # التحقق من المفتاح
        is_valid, metadata = LicenseManager.verify_serial(serial, hwid)
        
        if is_valid:
            # حفظ بيانات الترخيص
            license_data = {
                "serial": serial,
                "hwid": hwid,
                "activated_at": metadata.get("timestamp"),
                "status": "active"
            }
            
            if LicenseManager.save_license(license_data):
                QMessageBox.information(
                    self,
                    "✅ نجح التفعيل",
                    "تم تفعيل البرنامج بنجاح! شكراً لاستخدامك SmartFileRenamer"
                )
                self.activation_success.emit()
                self.accept()
            else:
                QMessageBox.critical(self, "❌ خطأ", "فشل حفظ بيانات التفعيل")
        else:
            QMessageBox.critical(
                self,
                "❌ خطأ في التفعيل",
                "مفتاح التفعيل غير صحيح أو لا يتطابق مع جهازك"
            )
        
        self.progress_bar.setVisible(False)
        self.activate_btn.setEnabled(True)
