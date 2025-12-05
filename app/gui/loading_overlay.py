"""Loading overlay widget for blocking operations."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen


class SpinnerWidget(QWidget):
    """Animated spinner widget."""
    
    def __init__(self, parent=None):
        """Initialize spinner."""
        super().__init__(parent)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self.setFixedSize(50, 50)
    
    def _rotate(self):
        """Rotate the spinner."""
        self._angle = (self._angle + 30) % 360
        self.update()
    
    def start(self):
        """Start the spinner animation."""
        self._timer.start(50)
    
    def stop(self):
        """Stop the spinner animation."""
        self._timer.stop()
    
    def paintEvent(self, event):
        """Paint the spinner."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        size = min(self.width(), self.height())
        center = size // 2
        radius = size // 2 - 5
        
        painter.translate(center, center)
        painter.rotate(self._angle)
        
        for i in range(12):
            painter.rotate(30)
            alpha = int(255 * (i + 1) / 12)
            pen = QPen(QColor(70, 130, 180, alpha))
            pen.setWidth(3)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(0, -radius + 10, 0, -radius)


class LoadingOverlay(QWidget):
    """Semi-transparent loading overlay with spinner."""
    
    def __init__(self, parent=None):
        """Initialize loading overlay."""
        super().__init__(parent)
        self._message = "Loading..."
        self._setupUi()
        self.hide()
    
    def _setupUi(self):
        """Set up the overlay UI."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Container for centered content
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 220);
                border-radius: 15px;
            }
        """)
        self.container.setMinimumWidth(250)
        containerLayout = QVBoxLayout(self.container)
        containerLayout.setContentsMargins(40, 30, 40, 30)
        containerLayout.setSpacing(15)
        containerLayout.setAlignment(Qt.AlignCenter)
        
        # Spinner
        self.spinner = SpinnerWidget()
        containerLayout.addWidget(self.spinner, 0, Qt.AlignCenter)
        
        # Message label
        self.messageLabel = QLabel(self._message)
        self.messageLabel.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.messageLabel.setAlignment(Qt.AlignCenter)
        self.messageLabel.setMinimumWidth(170)
        containerLayout.addWidget(self.messageLabel)
        
        layout.addWidget(self.container)
        self.setLayout(layout)
    
    def setMessage(self, message: str):
        """
        Set the loading message.
        
        Args:
            message: Message to display
        """
        self._message = message
        self.messageLabel.setText(message)
        self.messageLabel.adjustSize()
        self.container.adjustSize()
    
    def showOverlay(self, message: str = "Loading..."):
        """
        Show the loading overlay.
        
        Args:
            message: Message to display
        """
        self.setMessage(message)
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.spinner.start()
        self.show()
        self.raise_()
    
    def hideOverlay(self):
        """Hide the loading overlay."""
        self.spinner.stop()
        self.hide()
    
    def paintEvent(self, event):
        """Paint semi-transparent background."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
        super().paintEvent(event)
    
    def resizeEvent(self, event):
        """Handle resize to match parent."""
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect())

