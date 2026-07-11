"""
Theme Engine Module
نظام الثيمات المظلمة والفاتحة
"""

from PyQt6.QtGui import QColor, QFont
from typing import Dict


class ThemeEngine:
    """محرك الثيمات"""
    
    # ألوان الثيم الداكن
    DARK_THEME = {
        "primary_bg": "#1e1e1e",
        "secondary_bg": "#2d2d2d",
        "tertiary_bg": "#3d3d3d",
        "primary_text": "#ffffff",
        "secondary_text": "#b0b0b0",
        "accent": "#00a8ff",
        "accent_hover": "#0091d6",
        "success": "#4ade80",
        "warning": "#fbbf24",
        "error": "#f87171",
        "border": "#404040",
    }
    
    # ألوان الثيم الفاتح
    LIGHT_THEME = {
        "primary_bg": "#ffffff",
        "secondary_bg": "#f5f5f5",
        "tertiary_bg": "#eeeeee",
        "primary_text": "#1a1a1a",
        "secondary_text": "#666666",
        "accent": "#0066cc",
        "accent_hover": "#0052a3",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "border": "#e0e0e0",
    }
    
    def __init__(self, theme_name: str = "dark"):
        """
        تهيئة محرك الثيمات
        
        Args:
            theme_name: "dark" أو "light"
        """
        self.theme_name = theme_name
        self.current_theme = self.DARK_THEME if theme_name == "dark" else self.LIGHT_THEME
    
    def get_stylesheet(self) -> str:
        """الحصول على CSS الثيم كاملاً"""
        theme = self.current_theme
        
        stylesheet = f"""
            QMainWindow {{
                background-color: {theme['primary_bg']};
                color: {theme['primary_text']};
            }}
            
            QWidget {{
                background-color: {theme['primary_bg']};
                color: {theme['primary_text']};
            }}
            
            QLabel {{
                color: {theme['primary_text']};
            }}
            
            QPushButton {{
                background-color: {theme['accent']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            
            QPushButton:hover {{
                background-color: {theme['accent_hover']};
            }}
            
            QPushButton:pressed {{
                background-color: {theme['secondary_text']};
            }}
            
            QPushButton:disabled {{
                background-color: {theme['tertiary_bg']};
                color: {theme['secondary_text']};
            }}
            
            QLineEdit {{
                background-color: {theme['secondary_bg']};
                color: {theme['primary_text']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }}
            
            QLineEdit:focus {{
                border: 2px solid {theme['accent']};
            }}
            
            QTextEdit {{
                background-color: {theme['secondary_bg']};
                color: {theme['primary_text']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }}
            
            QTextEdit:focus {{
                border: 2px solid {theme['accent']};
            }}
            
            QComboBox {{
                background-color: {theme['secondary_bg']};
                color: {theme['primary_text']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
                padding: 6px;
                font-size: 11px;
            }}
            
            QComboBox:focus {{
                border: 2px solid {theme['accent']};
            }}
            
            QComboBox::drop-down {{
                border: none;
            }}
            
            QListWidget {{
                background-color: {theme['secondary_bg']};
                color: {theme['primary_text']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
            }}
            
            QListWidget::item:selected {{
                background-color: {theme['accent']};
            }}
            
            QTableWidget {{
                background-color: {theme['secondary_bg']};
                color: {theme['primary_text']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
            }}
            
            QTableWidget::item:selected {{
                background-color: {theme['accent']};
            }}
            
            QHeaderView::section {{
                background-color: {theme['tertiary_bg']};
                color: {theme['primary_text']};
                padding: 6px;
                border: none;
            }}
            
            QScrollBar:vertical {{
                background-color: {theme['secondary_bg']};
                width: 12px;
                border: none;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {theme['tertiary_bg']};
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {theme['accent']};
            }}
            
            QScrollBar:horizontal {{
                background-color: {theme['secondary_bg']};
                height: 12px;
                border: none;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {theme['tertiary_bg']};
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {theme['accent']};
            }}
            
            QDialog {{
                background-color: {theme['primary_bg']};
            }}
            
            QMessageBox {{
                background-color: {theme['primary_bg']};
            }}
            
            QProgressBar {{
                background-color: {theme['secondary_bg']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
                color: {theme['primary_text']};
                height: 20px;
            }}
            
            QProgressBar::chunk {{
                background-color: {theme['success']};
                border-radius: 3px;
            }}
        """
        
        return stylesheet
    
    def get_color(self, color_key: str) -> str:
        """الحصول على لون معين"""
        return self.current_theme.get(color_key, "#ffffff")
    
    def get_qcolor(self, color_key: str) -> QColor:
        """الحصول على QColor"""
        return QColor(self.get_color(color_key))
    
    def switch_theme(self, theme_name: str):
        """التبديل بين الثيمات"""
        if theme_name in ["dark", "light"]:
            self.theme_name = theme_name
            self.current_theme = (self.DARK_THEME if theme_name == "dark" 
                                 else self.LIGHT_THEME)
            return True
        return False
    
    def get_current_theme_name(self) -> str:
        """الحصول على اسم الثيم الحالي"""
        return self.theme_name
