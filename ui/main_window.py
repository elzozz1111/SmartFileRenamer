"""
Main Window
النافذة الرئيسية للتطبيق
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMessageBox,
    QProgressBar, QTabWidget, QTableWidget, QTableWidgetItem,
    QFileDialog, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor
from pathlib import Path
from ui.animated_button import AnimatedButton
from ui.theme_engine import ThemeEngine
from core.ai_engine import AIEngine
from core.db_manager import DatabaseManager
from core.workers import RenameWorker, CopyWorker
import os


class MainWindow(QMainWindow):
    """النافذة الرئيسية"""
    
    def __init__(self, theme_engine: ThemeEngine):
        """تهيئة النافذة الرئيسية"""
        super().__init__()
        self.theme_engine = theme_engine
        self.ai_engine = AIEngine()
        self.db_manager = DatabaseManager()
        self.rename_worker = None
        self.copy_worker = None
        
        self.setWindowTitle("SmartFileRenamer 🚀")
        self.setGeometry(50, 50, 1000, 700)
        self.setStyleSheet(theme_engine.get_stylesheet())
        
        self.setup_ui()
        self.load_statistics()
    
    def setup_ui(self):
        """بناء الواجهة الرئيسية"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # رأس الصفحة
        header = QLabel("🎯 SmartFileRenamer - إعادة تسمية ذكية للملفات")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        main_layout.addWidget(header)
        
        # تبويبات
        tabs = QTabWidget()
        
        # تبويب إعادة التسمية
        tabs.addTab(self.create_rename_tab(), "📝 إعادة التسمية")
        
        # تبويب السجل
        tabs.addTab(self.create_history_tab(), "📋 السجل")
        
        # تبويب الإحصائيات
        tabs.addTab(self.create_stats_tab(), "📊 الإحصائيات")
        
        # تبويب الإعدادات
        tabs.addTab(self.create_settings_tab(), "⚙️ الإعدادات")
        
        main_layout.addWidget(tabs)
        
        # شريط الحالة
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("✅ جاهز")
    
    def create_rename_tab(self) -> QWidget:
        """إنشاء تبويب إعادة التسمية"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # اختيار المجلد
        folder_layout = QHBoxLayout()
        folder_label = QLabel("المجلد:")
        self.folder_path = QLineEdit()
        self.folder_path.setReadOnly(True)
        self.folder_btn = AnimatedButton("📂 اختيار المجلد")
        self.folder_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_path)
        folder_layout.addWidget(self.folder_btn)
        layout.addLayout(folder_layout)
        
        # قائمة الملفات
        file_label = QLabel("📄 الملفات:")
        self.file_list = QListWidget()
        layout.addWidget(file_label)
        layout.addWidget(self.file_list)
        
        # نمط إع��دة التسمية
        pattern_layout = QHBoxLayout()
        pattern_label = QLabel("النمط:")
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems([
            "اقتراحات الذكاء الاصطناعي",
            "camelCase",
            "snake_case",
            "UPPERCASE",
            "lowercase"
        ])
        pattern_layout.addWidget(pattern_label)
        pattern_layout.addWidget(self.pattern_combo)
        layout.addLayout(pattern_layout)
        
        # أزرار التحكم
        button_layout = QHBoxLayout()
        
        self.suggest_btn = AnimatedButton("💡 اقتراحات")
        self.suggest_btn.clicked.connect(self.generate_suggestions)
        button_layout.addWidget(self.suggest_btn)
        
        self.rename_btn = AnimatedButton("✅ تطبيق التسمية")
        self.rename_btn.clicked.connect(self.apply_renaming)
        button_layout.addWidget(self.rename_btn)
        
        self.copy_btn = AnimatedButton("📋 نسخ")
        self.copy_btn.clicked.connect(self.copy_files)
        button_layout.addWidget(self.copy_btn)
        
        layout.addLayout(button_layout)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        return widget
    
    def create_history_tab(self) -> QWidget:
        """إنشاء تبويب السجل"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        history_label = QLabel("📋 سجل العمليات:")
        history_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(history_label)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "الاسم القديم",
            "الاسم الجديد",
            "المسار",
            "الحجم",
            "الوقت"
        ])
        layout.addWidget(self.history_table)
        
        return widget
    
    def create_stats_tab(self) -> QWidget:
        """إنشاء تبويب الإحصائيات"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        stats_label = QLabel("📊 الإحصائيات:")
        stats_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(stats_label)
        
        self.total_label = QLabel()
        self.today_label = QLabel()
        self.db_label = QLabel()
        
        layout.addWidget(self.total_label)
        layout.addWidget(self.today_label)
        layout.addWidget(self.db_label)
        layout.addStretch()
        
        return widget
    
    def create_settings_tab(self) -> QWidget:
        """إنشاء تبويب الإعدادات"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # الثيم
        theme_label = QLabel("🎨 الثيم:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["داكن", "فاتح"])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        layout.addWidget(theme_label)
        layout.addWidget(self.theme_combo)
        
        # OpenAI API Key
        api_label = QLabel("🔑 OpenAI API Key (اختياري):")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("sk-...")
        layout.addWidget(api_label)
        layout.addWidget(self.api_key_input)
        
        layout.addStretch()
        
        return widget
    
    def select_folder(self):
        """اختيار مجلد"""
        folder = QFileDialog.getExistingDirectory(self, "اختر مجلداً")
        if folder:
            self.folder_path.setText(folder)
            self.load_files(folder)
            self.status_bar.showMessage(f"✅ تم تحميل المجلد: {folder}")
    
    def load_files(self, folder: str):
        """تحميل الملفات من المجلد"""
        self.file_list.clear()
        try:
            folder_path = Path(folder)
            for file_path in folder_path.glob("*"):
                if file_path.is_file():
                    item = QListWidgetItem(file_path.name)
                    item.setData(Qt.ItemDataRole.UserRole, str(file_path))
                    self.file_list.addItem(item)
        except Exception as e:
            self.status_bar.showMessage(f"❌ خطأ: {e}")
    
    def generate_suggestions(self):
        """توليد اقتراحات الأسماء"""
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "⚠️ تحذير", "لم يتم تحميل أي ملفات")
            return
        
        self.status_bar.showMessage("⏳ جاري توليد الاقتراحات...")
        self.suggest_btn.setEnabled(False)
        
        # قائمة بأسماء الملفات
        file_names = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        
        # توليد الاقتراحات
        suggestions = self.ai_engine.batch_rename_suggestions(file_names)
        
        # عرض الاقتراحات
        QMessageBox.information(
            self,
            "💡 الاقتراحات",
            "تم توليد الاقتراحات بنجاح!"
        )
        
        self.suggest_btn.setEnabled(True)
        self.status_bar.showMessage("✅ تم توليد الاقتراحات")
    
    def apply_renaming(self):
        """تطبيق إعادة التسمية"""
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "⚠️ تحذير", "لا توجد ملفات للتسمية")
            return
        
        # إنشاء خريطة الأسماء
        rename_map = {}
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            old_path = item.data(Qt.ItemDataRole.UserRole)
            rename_map[old_path] = old_path  # يمكن تعديل هنا
        
        # بدء العملية
        self.rename_worker = RenameWorker(rename_map, self.db_manager)
        self.rename_worker.progress.connect(self.update_progress)
        self.rename_worker.status.connect(self.update_status)
        self.rename_worker.finished.connect(self.on_rename_finished)
        self.rename_worker.start()
        
        self.progress_bar.setVisible(True)
        self.rename_btn.setEnabled(False)
    
    def copy_files(self):
        """نسخ الملفات"""
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "⚠️ تحذير", "لا توجد ملفات للنسخ")
            return
        
        dest = QFileDialog.getExistingDirectory(self, "اختر مجلد الوجهة")
        if not dest:
            return
        
        # قائمة الملفات
        files = [self.file_list.item(i).data(Qt.ItemDataRole.UserRole) 
                for i in range(self.file_list.count())]
        
        # بدء النسخ
        self.copy_worker = CopyWorker(files, dest)
        self.copy_worker.progress.connect(self.update_progress)
        self.copy_worker.status.connect(self.update_status)
        self.copy_worker.finished.connect(self.on_copy_finished)
        self.copy_worker.start()
        
        self.progress_bar.setVisible(True)
        self.copy_btn.setEnabled(False)
    
    def update_progress(self, value: int):
        """تحديث شريط التقدم"""
        self.progress_bar.setValue(value)
    
    def update_status(self, message: str):
        """تحديث رسالة الحالة"""
        self.status_bar.showMessage(message)
    
    def on_rename_finished(self, success: bool):
        """عند انتهاء عملية إعادة التسمية"""
        self.progress_bar.setVisible(False)
        self.rename_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "✅ نجح", "تم إعادة التسمية بنجاح")
            self.load_statistics()
        
        self.status_bar.showMessage("✅ انتهت العملية")
    
    def on_copy_finished(self, success: bool):
        """عند انتهاء عملية النسخ"""
        self.progress_bar.setVisible(False)
        self.copy_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "✅ نجح", "تم النسخ بنجاح")
    
    def load_statistics(self):
        """تحميل الإحصائيات"""
        stats = self.db_manager.get_statistics()
        self.total_label.setText(f"📊 إجمالي العمليات: {stats.get('total_renames', 0)}")
        self.today_label.setText(f"📅 عمليات اليوم: {stats.get('today_renames', 0)}")
        self.db_label.setText(f"💾 قاعدة البيانات: {stats.get('database_file', 'N/A')}")
    
    def change_theme(self, index: int):
        """تبديل الثيم"""
        theme_name = "dark" if index == 0 else "light"
        self.theme_engine.switch_theme(theme_name)
        self.setStyleSheet(self.theme_engine.get_stylesheet())
        self.status_bar.showMessage(f"✅ تم تغيير الثيم إلى {theme_name}")
