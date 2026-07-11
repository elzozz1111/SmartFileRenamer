"""
Animated Button Widget
زر متحرك بتأثيرات انتقالية سلسة
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect, Qt
from PyQt6.QtGui import QColor, QFont


class AnimatedButton(QPushButton):
    """زر متحرك مع تأثيرات"""
    
    def __init__(self, text: str = "", parent=None):
        """تهيئة الزر"""
        super().__init__(text, parent)
        self.animation = None
        self.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def start_animation(self):
        """بدء تأثير التحريك"""
        if self.animation:
            self.animation.stop()
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.geometry())
        
        # تقليل الحجم قليلاً
        new_rect = self.geometry()
        new_rect.setX(new_rect.x() + 2)
        new_rect.setY(new_rect.y() + 2)
        new_rect.setWidth(new_rect.width() - 4)
        new_rect.setHeight(new_rect.height() - 4)
        
        self.animation.setEndValue(new_rect)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.animation.finished.connect(self.restore_animation)
        self.animation.start()
    
    def restore_animation(self):
        """استعادة حالة الزر الأصلية"""
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(200)
        animation.setStartValue(self.geometry())
        animation.setEndValue(self.geometry())
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        animation.start()
    
    def mousePressEvent(self, event):
        """عند الضغط على الزر"""
        self.start_animation()
        super().mousePressEvent(event)
