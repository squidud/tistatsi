from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor

class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        
        # Animation properties
        self._bg_color = QColor("#69E3B4")
        self._hover_color = QColor("#5AC8A1")
        
        # Set initial style
        self.setStyleSheet("""
            QPushButton {
                background-color: #69E3B4;
                color: #595959;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        
        # Create color animation
        self._color_animation = QPropertyAnimation(self, b"bg_color")
        self._color_animation.setDuration(200)
        self._color_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    @pyqtProperty(QColor)
    def bg_color(self):
        return self._bg_color
    
    @bg_color.setter
    def bg_color(self, color):
        self._bg_color = color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                color: #595959;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }}
        """)

    def enterEvent(self, event):
        # Stop any running animation
        self._color_animation.stop()
        
        # Color animation to hover color
        self._color_animation.setStartValue(self._bg_color)
        self._color_animation.setEndValue(self._hover_color)
        self._color_animation.start()
        
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Stop any running animation
        self._color_animation.stop()
        
        # Color animation back to normal
        self._color_animation.setStartValue(self._bg_color)
        self._color_animation.setEndValue(QColor("#69E3B4"))
        self._color_animation.start()
        
        super().leaveEvent(event)