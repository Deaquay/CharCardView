"""Flow layout widget for wrapping items like tags."""

from PySide6.QtWidgets import QLayout, QSizePolicy
from PySide6.QtCore import Qt, QRect, QSize, QPoint


class FlowLayout(QLayout):
    """A layout that arranges widgets in a flowing manner, wrapping to new lines."""
    
    def __init__(self, parent=None, margin=0, hSpacing=5, vSpacing=5):
        """
        Initialize flow layout.
        
        Args:
            parent: Parent widget
            margin: Layout margin
            hSpacing: Horizontal spacing between items
            vSpacing: Vertical spacing between rows
        """
        super().__init__(parent)
        self._hSpacing = hSpacing
        self._vSpacing = vSpacing
        self._items = []
        
        if margin >= 0:
            self.setContentsMargins(margin, margin, margin, margin)
    
    def addItem(self, item):
        """Add an item to the layout."""
        self._items.append(item)
    
    def horizontalSpacing(self) -> int:
        """Get horizontal spacing."""
        return self._hSpacing
    
    def verticalSpacing(self) -> int:
        """Get vertical spacing."""
        return self._vSpacing
    
    def count(self) -> int:
        """Get number of items."""
        return len(self._items)
    
    def itemAt(self, index: int):
        """Get item at index."""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
    
    def takeAt(self, index: int):
        """Remove and return item at index."""
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None
    
    def expandingDirections(self):
        """Return expanding directions."""
        return Qt.Orientations()
    
    def hasHeightForWidth(self) -> bool:
        """Height depends on width."""
        return True
    
    def heightForWidth(self, width: int) -> int:
        """Calculate height for given width."""
        return self._doLayout(QRect(0, 0, width, 0), True)
    
    def setGeometry(self, rect: QRect):
        """Set layout geometry."""
        super().setGeometry(rect)
        self._doLayout(rect, False)
    
    def sizeHint(self) -> QSize:
        """Return size hint."""
        return self.minimumSize()
    
    def minimumSize(self) -> QSize:
        """Return minimum size."""
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size
    
    def _doLayout(self, rect: QRect, testOnly: bool) -> int:
        """
        Perform the layout.
        
        Args:
            rect: Available rectangle
            testOnly: If True, only calculate height without moving widgets
            
        Returns:
            Height of the laid out content
        """
        margins = self.contentsMargins()
        effectiveRect = rect.adjusted(margins.left(), margins.top(), -margins.right(), -margins.bottom())
        
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0
        
        for item in self._items:
            widget = item.widget()
            if widget is None:
                continue
            
            spaceX = self._hSpacing
            spaceY = self._vSpacing
            
            nextX = x + item.sizeHint().width() + spaceX
            
            if nextX - spaceX > effectiveRect.right() and lineHeight > 0:
                x = effectiveRect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        
        return y + lineHeight - rect.y() + margins.bottom()

